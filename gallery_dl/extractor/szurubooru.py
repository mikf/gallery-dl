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

    def _init(self):
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
    "bcbnsfw": {
        "root": "https://booru.bcbnsfw.space",
        "pattern": r"booru\.bcbnsfw\.space",
        "query-all": "*",
    },
    "snootbooru": {
        "root": "https://snootbooru.com",
        "pattern": r"snootbooru\.com",
    },
    "visuabusters": {
        "root": "https://www.visuabusters.com/booru",
        "pattern": r"(?:www\.)?visuabusters\.com/booru",
    },
})


class SzurubooruTagExtractor(SzurubooruExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}_{version}"
    pattern = BASE_PATTERN + r"/posts(?:/query=([^/?#]*))?"
    example = "https://booru.bcbnsfw.space/posts/query=TAG"

    def __init__(self, match):
        SzurubooruExtractor.__init__(self, match)
        query = self.groups[-1]
        self.query = text.unquote(query.replace("+", " ")) if query else ""

    def metadata(self):
        return {"search_tags": self.query}

    def posts(self):
        if self.query.strip():
            query = self.query
        else:
            query = self.config_instance("query-all")

        return self._pagination("/posts/", {"query": query})


class SzurubooruPostExtractor(SzurubooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}_{version}"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    example = "https://booru.bcbnsfw.space/post/12345"

    def posts(self):
        return (self._api_request("/post/" + self.groups[-1]),)
