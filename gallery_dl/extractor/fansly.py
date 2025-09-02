# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fansly.com/"""

from .common import Extractor, Message
from .. import text
import time

BASE_PATTERN = r"(?:https?://)?(?:www\.)?fansly\.com"


class FanslyExtractor(Extractor):
    """Base class for fansly extractors"""
    category = "fansly"
    root = "https://fansly.com"
    directory_fmt = ("{category}", "{account[username]} ({account[id]})")
    filename_fmt = "{id}_{num}_{file[id]}.{extension}"
    archive_fmt = "{file[id]}"

    def _init(self):
        self.api = FanslyAPI(self)

    def items(self):
        for post in self.posts():
            files = self._extract_files(post)
            post["count"] = len(files)
            post["date"] = text.parse_timestamp(post["createdAt"])

            yield Message.Directory, post
            for post["num"], file in enumerate(files, 1):
                post.update(file)
                url = file["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def _extract_files(self, post):
        files = []

        for attachment in post.pop("attachments"):
            media = attachment["media"]
            file = {
                **media,
                "date": text.parse_timestamp(media["createdAt"]),
                "date_updated": text.parse_timestamp(media["updatedAt"]),
            }

            width = 0
            for variant in media["variants"]:
                if variant["width"] > width:
                    width = variant["width"]
                    variant_max = variant
                if variant["type"] == 303:
                    break
            else:
                # image
                file["type"] = "image"
                files.append({
                    "file": file,
                    "url" : variant_max["locations"][0]["location"],
                })
                continue

            # video
            location = variant["locations"][0]
            meta = location["metadata"]

            file["type"] = "video"
            files.append({
                "file": file,
                "url": f"ytdl:{location['location']}",
                "_fallback": (media["locations"][0]["location"],),
                "_ytdl_manifest": "dash",
                "_ytdl_manifest_cookies": (
                    ("CloudFront-Key-Pair-Id", meta["Key-Pair-Id"]),
                    ("CloudFront-Signature"  , meta["Signature"]),
                    ("CloudFront-Policy"     , meta["Policy"]),
                ),
            })

        return files


class FanslyPostExtractor(FanslyExtractor):
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/post/(\d+)"
    example = "https://fansly.com/post/1234567890"

    def posts(self):
        return self.api.post(self.groups[0])


class FanslyHomeExtractor(FanslyExtractor):
    subcategory = "home"
    pattern = rf"{BASE_PATTERN}/home(?:/(subscribed|list/(\d+)))?"
    example = "https://fansly.com/home"

    def items(self):
        pass


class FanslyListExtractor(FanslyExtractor):
    subcategory = "list"
    pattern = rf"{BASE_PATTERN}/lists/(\d+)"
    example = "https://fansly.com/lists/1234567890"

    def items(self):
        pass


class FanslyCreatorPostsExtractor(FanslyExtractor):
    subcategory = "creator-posts"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/posts"
    example = "https://fansly.com/CREATOR/posts"

    def posts(self):
        account = self.api.account(self.groups[0])
        wall_id = account["walls"][0]["id"]
        return self.api.timeline_new(account["id"], wall_id)


class FanslyAPI():
    ROOT = "https://apiv3.fansly.com"

    def __init__(self, extractor):
        self.extractor = extractor

        token = extractor.config("token")
        if not token:
            self.extractor.log.warning("No 'token' provided")

        self.headers = {
            "fansly-client-ts": None,
            "Origin"          : extractor.root,
            "authorization"   : token,
        }

    def account(self, username):
        endpoint = "/v1/account"
        params = {"usernames": username}
        return self._call(endpoint, params)["response"][0]

    def post(self, post_id):
        endpoint = "/v1/post"
        params = {"ids": post_id}
        return self._update_posts(self._call(endpoint, params))

    def timeline_new(self, account_id, wall_id):
        endpoint = f"/v1/timelinenew/{account_id}"
        params = {
            "before"       : "0",
            "after"        : "0",
            "wallId"       : wall_id,
            "contentSearch": "",
        }
        return self._pagination(endpoint, params)

    def _update_posts(self, data):
        response = data["response"]
        accounts = {
            account["id"]: account
            for account in response["accounts"]
        }
        media = {
            media["id"]: media
            for media in response["accountMedia"]
        }
        bundles = {
            bundle["id"]: bundle
            for bundle in response["accountMediaBundles"]
        }

        posts = response["posts"]
        for post in posts:
            post["account"] = accounts[post.pop("accountId")]
            att = []

            for attachment in post["attachments"]:
                cid = attachment["contentId"]
                if cid in media:
                    att.append(media[cid])
                elif cid in bundles:
                    content = bundles[cid]["bundleContent"]
                    content.sort(key=lambda c: c["pos"])
                    att.extend(
                        media[c["accountMediaId"]]
                        for c in content
                    )
            post["attachments"] = att
        return posts

    def _call(self, endpoint, params):
        url = f"{self.ROOT}/api{endpoint}"
        params["ngsw-bypass"] = "true"
        headers = self.headers.copy()
        headers["fansly-client-ts"] = str(int(time.time() * 1000))

        return self.extractor.request_json(url, params=params, headers=headers)

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)

            posts = self._update_posts(data)
            if not posts:
                return
            yield from posts

            params["before"] = min(p["id"] for p in posts)
