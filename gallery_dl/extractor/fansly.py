# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fansly.com/"""

from .common import Extractor, Message
from .. import text, util, exception
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

        if fmts := self.config("formats"):
            self.formats = set(fmts)
        else:
            self.formats = {1, 2, 3, 4, 302, 303}

    def items(self):
        for post in self.posts():
            files = self._extract_files(post)
            post["count"] = len(files)
            post["date"] = self.parse_timestamp(post["createdAt"])

            yield Message.Directory, "", post
            for post["num"], file in enumerate(files, 1):
                post.update(file)
                url = file["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def posts(self):
        creator, wall_id = self.groups
        account = self.api.account(creator)
        walls = account["walls"]

        if wall_id:
            for wall in walls:
                if wall["id"] == wall_id:
                    break
            else:
                raise exception.NotFoundError("wall")
            walls = (wall,)

        for wall in walls:
            self.kwdict["wall"] = wall
            yield from self.posts_wall(account, wall)

    def _extract_files(self, post):
        if "attachments" not in post:
            return ()

        if "_extra" in post:
            extra = post.pop("_extra", ())
            media = {
                media["id"]: media
                for media in self.api.account_media(extra)
            }
            post["attachments"].extend(
                media[mid]
                for mid in extra
                if mid in media
            )

        files = []
        for attachment in post.pop("attachments"):
            try:
                self._extract_attachment(files, post, attachment)
            except Exception as exc:
                self.log.traceback(exc)
                self.log.error(
                    "%s/%s, Failed to extract media (%s: %s)",
                    post["id"], attachment.get("id"),
                    exc.__class__.__name__, exc)
        return files

    def _extract_attachment(self, files, post, attachment):
        media = attachment["media"]

        variants = media.pop("variants") or []
        if media.get("locations"):
            variants.append(media)

        formats = [
            (variant["width"], (type-500 if type > 256 else type), variant)
            for variant in variants
            if variant.get("locations") and
            (type := variant["type"]) in self.formats
        ]

        try:
            variant = max(formats)[-1]
        except Exception:
            return self.log.warning("%s/%s: No format available",
                                    post["id"], attachment["id"])

        mime = variant["mimetype"]
        location = variant.pop("locations")[0]
        if "metadata" in variant:
            try:
                variant.update(util.json_loads(variant.pop("metadata")))
            except Exception:
                pass

        file = {
            **variant,
            "format": variant["type"],
            "date": self.parse_timestamp(media["createdAt"]),
            "date_updated": self.parse_timestamp(media["updatedAt"]),
        }

        if "metadata" in location:
            # manifest
            meta = location["metadata"]
            file["type"] = "video"

            try:
                fallback = (media["locations"][0]["location"],)
            except Exception:
                fallback = ()

            files.append({
                "file": file,
                "url": f"ytdl:{location['location']}",
                "_fallback": fallback,
                "_ytdl_manifest":
                    "dash" if mime == "application/dash+xml" else "hls",
                "_ytdl_manifest_cookies": (
                    ("CloudFront-Key-Pair-Id", meta["Key-Pair-Id"]),
                    ("CloudFront-Signature"  , meta["Signature"]),
                    ("CloudFront-Policy"     , meta["Policy"]),
                ),
            })
        else:
            file["type"] = "image" if mime.startswith("image/") else "video"
            files.append({
                "file": file,
                "url" : location["location"],
            })


class FanslyPostExtractor(FanslyExtractor):
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/post/(\d+)"
    example = "https://fansly.com/post/1234567890"

    def posts(self):
        return self.api.post(self.groups[0])


class FanslyHomeExtractor(FanslyExtractor):
    subcategory = "home"
    pattern = rf"{BASE_PATTERN}/home(?:/(?:subscribed()|list/(\d+)))?"
    example = "https://fansly.com/home"

    def posts(self):
        subscribed, list_id = self.groups
        if subscribed is not None:
            mode = "1"
        elif list_id is not None:
            mode = None
        else:
            mode = "0"
        return self.api.timeline_home(mode, list_id)


class FanslyListExtractor(FanslyExtractor):
    subcategory = "list"
    pattern = rf"{BASE_PATTERN}/lists/(\d+)"
    example = "https://fansly.com/lists/1234567890"

    def items(self):
        base = f"{self.root}/"
        for account in self.api.lists_itemsnew(self.groups[0]):
            account["_extractor"] = FanslyCreatorPostsExtractor
            url = f"{base}{account['username']}/posts"
            yield Message.Queue, url, account


class FanslyListsExtractor(FanslyExtractor):
    subcategory = "lists"
    pattern = rf"{BASE_PATTERN}/lists"
    example = "https://fansly.com/lists"

    def items(self):
        base = f"{self.root}/lists/"
        for list in self.api.lists_account():
            list["_extractor"] = FanslyListExtractor
            url = f"{base}{list['id']}#{list['label']}"
            yield Message.Queue, url, list


class FanslyCreatorPostsExtractor(FanslyExtractor):
    subcategory = "creator-posts"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/posts(?:/wall/(\d+))?"
    example = "https://fansly.com/CREATOR/posts"

    def posts_wall(self, account, wall):
        return self.api.timeline_new(account["id"], wall["id"])


class FanslyCreatorMediaExtractor(FanslyExtractor):
    subcategory = "creator-media"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/media(?:/wall/(\d+))?"
    example = "https://fansly.com/CREATOR/media"

    def posts_wall(self, account, wall):
        return self.api.mediaoffers_location(account["id"], wall["id"])


class FanslyAPI():
    ROOT = "https://apiv3.fansly.com"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "fansly-client-ts": None,
            "Origin"          : extractor.root,
        }

        if token := extractor.config("token"):
            self.headers["authorization"] = token
            self.extractor.log.debug(
                "Using authorization 'token' %.5s...", token)
        else:
            self.extractor.log.warning("No 'token' provided")

    def account(self, creator):
        if creator.startswith("id:"):
            return self.account_by_id(creator[3:])
        return self.account_by_username(creator)

    def account_by_username(self, username):
        endpoint = "/v1/account"
        params = {"usernames": username}
        return self._call(endpoint, params)[0]

    def account_by_id(self, account_id):
        endpoint = "/v1/account"
        params = {"ids": account_id}
        return self._call(endpoint, params)[0]

    def accounts_by_id(self, account_ids):
        endpoint = "/v1/account"
        params = {"ids": ",".join(map(str, account_ids))}
        return self._call(endpoint, params)

    def account_media(self, media_ids):
        endpoint = "/v1/account/media"
        params = {"ids": ",".join(map(str, media_ids))}
        return self._call(endpoint, params)

    def lists_account(self):
        endpoint = "/v1/lists/account"
        params = {"itemId": ""}
        return self._call(endpoint, params)

    def lists_itemsnew(self, list_id, sort="3"):
        endpoint = "/v1/lists/itemsnew"
        params = {
            "listId"  : list_id,
            "limit"   : 50,
            "after"   : None,
            "sortMode": sort,
        }
        return self._pagination_list(endpoint, params)

    def mediaoffers_location(self, account_id, wall_id):
        endpoint = "/v1/mediaoffers/location"
        params = {
            "locationId": wall_id,
            "locationType": "1002",
            "accountId": account_id,
            "mediaType": "",
            "before": "",
            "after" : "0",
            "limit" : "30",
            "offset": "0",
        }
        return self._pagination_media(endpoint, params)

    def post(self, post_id):
        endpoint = "/v1/post"
        params = {"ids": post_id}
        return self._update_posts(self._call(endpoint, params))

    def timeline_home(self, mode="0", list_id=None):
        endpoint = "/v1/timeline/home"
        params = {"before": "0", "after": "0"}
        if list_id is None:
            params["mode"] = mode
        else:
            params["listId"] = list_id
        return self._pagination(endpoint, params)

    def timeline_new(self, account_id, wall_id):
        endpoint = f"/v1/timelinenew/{account_id}"
        params = {
            "before"       : "0",
            "after"        : "0",
            "wallId"       : wall_id,
            "contentSearch": "",
        }
        return self._pagination(endpoint, params)

    def _update_posts(self, response):
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
            try:
                post["account"] = accounts[post.pop("accountId")]
            except KeyError:
                pass

            extra = None
            attachments = []
            for attachment in post["attachments"]:
                try:
                    cid = attachment["contentId"]
                except KeyError:
                    attachments.append(attachment)
                    continue

                if cid in media:
                    attachments.append(media[cid])
                elif cid in bundles:
                    bundle = bundles[cid]["bundleContent"]
                    bundle.sort(key=lambda c: c["pos"])
                    for c in bundle:
                        mid = c["accountMediaId"]
                        if mid in media:
                            attachments.append(media[mid])
                        else:
                            if extra is None:
                                post["_extra"] = extra = []
                            extra.append(mid)
                else:
                    self.extractor.log.warning(
                        "%s: Unhandled 'contentId' %s",
                        post["id"], cid)
            post["attachments"] = attachments

        return posts

    def _update_media(self, items, response):
        posts = {
            post["id"]: post
            for post in response["posts"]
        }

        response["posts"] = [
            posts[item["correlationId"]]
            for item in items
        ]

        return self._update_posts(response)

    def _update_items(self, items):
        ids = [item["id"] for item in items]
        accounts = {
            account["id"]: account
            for account in self.accounts_by_id(ids)
        }
        return [accounts[id] for id in ids]

    def _call(self, endpoint, params):
        url = f"{self.ROOT}/api{endpoint}"
        params["ngsw-bypass"] = "true"
        headers = self.headers.copy()
        headers["fansly-client-ts"] = str(int(time.time() * 1000))

        data = self.extractor.request_json(
            url, params=params, headers=headers)
        return data["response"]

    def _pagination(self, endpoint, params):
        while True:
            response = self._call(endpoint, params)

            if not response.get("posts"):
                return
            posts = self._update_posts(response)
            yield from posts
            params["before"] = min(p["id"] for p in posts)

    def _pagination_list(self, endpoint, params):
        while True:
            response = self._call(endpoint, params)

            if not response:
                return
            yield from self._update_items(response)
            params["after"] = response[-1]["sortId"]

    def _pagination_media(self, endpoint, params):
        while True:
            response = self._call(endpoint, params)

            data = response["data"]
            if not data:
                return
            yield from self._update_media(data, response["aggregationData"])
            params["before"] = data[-1]["id"]
