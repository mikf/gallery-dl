# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for szurubooru instances"""

from . import booru
from .. import text

import collections
import binascii


class SzurubooruExtractor(booru.BooruExtractor):
    basecategory = "szurubooru"
    filename_fmt = "{id}_{version}_{checksumMD5}.{extension}"
    per_page = 100

    def __init__(self, match):
        booru.BooruExtractor.__init__(self, match)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        username = self.config("username")
        if username:
            token = self.config("token")
            if token:
                value = username + ":" + token
                self.headers["Authorization"] = "Token " + \
                    binascii.b2a_base64(value.encode())[:-1].decode()

    def _api_request(self, endpoint, params=None):
        url = self.root + "/api" + endpoint
        return self.request(url, headers=self.headers, params=params).json()

    def _pagination(self, endpoint, params):
        params["offset"] = 0
        params["limit"] = self.per_page

        while True:
            data = self._api_request(endpoint, params)
            results = data["results"]

            yield from results

            if len(results) < self.per_page:
                return
            params["offset"] += len(results)

    def _file_url(self, post):
        url = post["contentUrl"]
        if not url.startswith("http"):
            url = self.root + "/" + url
        return url

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_datetime(
            post["creationTime"], "%Y-%m-%dT%H:%M:%S.%fZ")

        tags = []
        append = tags.append
        tags_categories = collections.defaultdict(list)

        for tag in post["tags"]:
            tag_type = tag["category"].rpartition("_")[2]
            tag_name = tag["names"][0]
            tags_categories[tag_type].append(tag_name)
            append(tag_name)

        post["tags"] = tags
        for category, tags in tags_categories.items():
            post["tags_" + category] = tags


BASE_PATTERN = SzurubooruExtractor.update({
    "foalcon": {
        "root": "https://booru.foalcon.com",
        "pattern": r"booru\.foalcon\.com",
    },
    "bcbnsfw": {
        "root": "https://booru.bcbnsfw.space",
        "pattern": r"booru\.bcbnsfw\.space",
    },
})


class SzurubooruTagExtractor(SzurubooruExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}_{version}"
    pattern = BASE_PATTERN + r"/posts/query=([^/?#]+)"
    test = (
        ("https://booru.foalcon.com/posts/query=simple_background", {
            "pattern": r"https://booru\.foalcon\.com/data/posts"
                       r"/\d+_[0-9a-f]{16}\.\w+",
            "range": "1-150",
            "count": 150,
        }),
        ("https://booru.bcbnsfw.space/posts/query=simple_background"),
    )

    def __init__(self, match):
        SzurubooruExtractor.__init__(self, match)
        query = match.group(match.lastindex)
        self.query = text.unquote(query.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.query}

    def posts(self):
        return self._pagination("/posts/", {"query": self.query})


class SzurubooruPostExtractor(SzurubooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}_{version}"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    test = (
        ("https://booru.foalcon.com/post/30092", {
            "pattern": r"https://booru\.foalcon\.com/data/posts"
                       r"/30092_b7d56e941888b624\.png",
            "url": "dad4d4c67d87cd9a4ac429b3414747c27a95d5cb",
            "content": "86d1514c0ca8197950cc4b74e7a59b2dc76ebf9c",
        }),
        ("https://booru.bcbnsfw.space/post/1599", {
            "pattern": r"https://booru\.bcbnsfw\.space/data/posts"
                       r"/1599_53784518e92086bd\.png",
            "content": "0c38fc612ba1f03950fad31c4f80a1fccdab1096",
        }),
    )

    def __init__(self, match):
        SzurubooruExtractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        return (self._api_request("/post/" + self.post_id),)
