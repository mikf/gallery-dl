# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tungsten.run/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tungsten\.run"


class TungstenExtractor(Extractor):
    """Base class for tungsten extractors"""
    category = "tungsten"
    root = "https://tungsten.run"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{date} {title:?/ /}{uuid}.{extension}"
    archive_fmt = "{uuid}"

    def items(self):
        for post in self.posts():
            url = post["original_url"]
            post["date"] = self.parse_datetime_iso(post["created_at"])
            post["filename"] = url[url.rfind("/")+1:]
            post["extension"] = "webp"
            yield Message.Directory, "", post
            yield Message.Url, url, post

    def _pagination(self, url, params):
        params["page"] = 1
        params["per_page"] = 40

        headers = {
            "Origin": self.root,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }

        while True:
            data = self.request_json(url, params=params, headers=headers)

            yield from data

            if len(data) < params["per_page"]:
                break
            params["page"] += 1


class TungstenPostExtractor(TungstenExtractor):
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/post/(\w+)"
    example = "https://tungsten.run/post/AbCdEfGhIjKlMnOp"

    def posts(self):
        url = f"{self.root}/post/{self.groups[0]}"
        page = self.request(url).text
        data = self._extract_nextdata(page)
        return (data["props"]["pageProps"]["post"],)


class TungstenModelExtractor(TungstenExtractor):
    subcategory = "model"
    pattern = rf"{BASE_PATTERN}/model/(\w+)(?:/?\?model_version=(\w+))?"
    example = "https://tungsten.run/model/AbCdEfGhIjKlM"

    def posts(self):
        uuid_model, uuid_version = self.groups

        if uuid_version is None:
            url = f"{self.root}/model/{uuid_model}/"
            page = self.request(url).text
            uuid_version = text.extr(page, '"modelVersionUUID":"', '"')

        url = "https://api.tungsten.run/v1/posts"
        params = {
            "sort"          : "top_all_time",
            "tweakable_only": "false",
            "following"     : "false",
            "model_version_uuid": uuid_version,
        }
        return self._pagination(url, params)


class TungstenUserExtractor(TungstenExtractor):
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/user/([^/?#]+)(?:/posts)?/?(?:\?([^#]+))?"
    example = "https://tungsten.run/user/USER"

    def posts(self):
        user, qs = self.groups
        url = f"{self.root}/user/{user}"
        page = self.request(url).text
        uuid_user = text.extr(page, '"user":{"uuid":"', '"')

        url = f"https://api.tungsten.run/v1/users/{uuid_user}/posts"
        params = text.parse_query(qs)
        params.setdefault("sort", "top_all_time")
        self.kwdict["search_tags"] = params.get("tag", "")
        return self._pagination(url, params)
