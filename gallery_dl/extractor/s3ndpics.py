# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://s3nd.pics/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?s3nd\.pics"


class S3ndpicsExtractor(Extractor):
    """Base class for s3ndpics extractors"""
    category = "s3ndpics"
    root = "https://s3nd.pics"
    root_api = f"{root}/api"
    directory_fmt = ("{category}", "{user[username]}",
                     "{date} {title:?/ /}({id})")
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"

    def items(self):
        base = "https://s3.s3nd.pics/s3nd-pics/"

        for post in self.posts():
            post["id"] = post.pop("_id", None)
            post["user"] = post.pop("userId", None)
            post["date"] = self.parse_datetime_iso(post["createdAt"])
            post["date_updated"] = self.parse_datetime_iso(post["updatedAt"])

            files = post.pop("files", ())
            post["count"] = len(files)

            yield Message.Directory, "", post
            for post["num"], file in enumerate(files, 1):
                post["type"] = file["type"]
                path = file["url"]
                text.nameext_from_url(path, post)
                yield Message.Url, f"{base}{path}", post

    def _pagination(self, url, params):
        params["page"] = 1

        while True:
            data = self.request_json(url, params=params)

            self.kwdict["total"] = data["pagination"]["total"]
            yield from data["posts"]

            if params["page"] >= data["pagination"]["pages"]:
                return
            params["page"] += 1


class S3ndpicsPostExtractor(S3ndpicsExtractor):
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/post/([0-9a-f]+)"
    example = "https://s3nd.pics/post/0123456789abcdef01234567"

    def posts(self):
        url = f"{self.root_api}/posts/{self.groups[0]}"
        return (self.request_json(url)["post"],)


class S3ndpicsUserExtractor(S3ndpicsExtractor):
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/user/(\w+)"
    example = "https://s3nd.pics/user/USER"

    def posts(self):
        url = f"{self.root_api}/users/username/{self.groups[0]}"
        self.kwdict["user"] = user = self.request_json(url)["user"]

        url = f"{self.root_api}/posts"
        params = {
            "userId": user["_id"],
            "limit" : "12",
            "sortBy": "newest",
        }
        return self._pagination(url, params)


class S3ndpicsSearchExtractor(S3ndpicsExtractor):
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/search/?\?([^#]+)"
    example = "https://s3nd.pics/search?QUERY"

    def posts(self):
        url = f"{self.root_api}/posts"
        params = text.parse_query(self.groups[0])
        params.setdefault("limit", "20")
        self.kwdict["search_tags"] = \
            params.get("tag") or params.get("tags") or params.get("q")
        return self._pagination(url, params)
