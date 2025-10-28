# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fansly.com/"""

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?fansly\.com"


class FanslyExtractor(Extractor):
    """Base class for fansly extractors"""
    category = "fansly"
    root = "https://fansly.com"
    directory_fmt = ("{category}", "{account[username]} ({account[id]})")
    filename_fmt = "{id}_{num}_{file[id]}.{extension}"
    archive_fmt = "{file[id]}"

    def _init(self):
        self.api = self.utils().FanslyAPI(self)

        if fmts := self.config("formats"):
            self.formats = set(fmts)
        else:
            self.formats = {1, 2, 3, 4, 302, 303}

    def items(self):
        for post in self.posts():
            files = self._extract_files(post)
            post["count"] = len(files)
            post["date"] = self.parse_timestamp(post["createdAt"])

            yield Message.Directory, post
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
        files = []

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
