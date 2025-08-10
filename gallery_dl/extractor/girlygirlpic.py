# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://girlygirlpic.com"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = (r"(?:https?://)?([a-z]{2})\."
                r"(?:girlygirlpic\.com|girlgirlgo\.org)")


class GirlygirlpicExtractor(Extractor):
    category = "Girlygirlpic"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{num:>03}.{extension}"

    payload = {
        "action": "load_infinite_content",
        "next_params":
            "paged=0&posts_per_page=10&post_status=publish&category__in=0",
        "layout_type": "v3",
        "page_id": "pid407",
        "random_index": 0,
        "model_id": "",
        "company_id": "",
        "tag_id": "",
        "country_id": "",
        "type_tag": "Company",
        "search_keys_tag": ""
    }

    def _pagination(self, endpoint):
        url = f"https://{self.groups[0]}.girlygirlpic.com/api/{endpoint}"
        data = {"_extractor": GirlygirlpicAlbumExtractor}
        while True:
            json = self.request(url, method="POST", json=self.payload).json()
            if not json["new_posts"]:
                return
            self.payload["next_params"] = json["next_params"]
            urls = text.extract_iter(
                json["new_posts"],
                "entry-title\"><a class=on-popunder href=",
                ">"
            )
            for album in urls:
                yield Message.Queue, album, data


class GirlygirlpicAlbumExtractor(GirlygirlpicExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a/([a-zA-Z0-9]+)"
    example = "https://en.girlygirlpic.com/a/ALBUMID"

    def items(self):
        url = f"https://{self.groups[0]}.girlygirlpic.com/ax"
        payload = {"album_id": self.groups[1]}
        page = self.request(url, method="POST", json=payload).text
        extr = text.extract_from(page)
        urls = list(text.extract_iter(page, "link-w><a href=", " class"))
        data = {
            "title": text.unescape(extr("<li><span>", "</span>")),
            "date": text.parse_datetime(
                extr("datetime=", ">"), "%Y-%m-%dT%H:%M:%S"),
            "model": extr("rel=author>", "</a>"),
            "tags": list(text.extract_iter(page, 'tag">', "</a>")),
            "count": len(urls),
            "album_id": self.groups[1]
        }

        yield Message.Directory, data
        for data["num"], image in enumerate(urls, 1):
            text.nameext_from_url(image, data)
            yield Message.Url, image, data


class GirlygirlpicModelExtractor(GirlygirlpicExtractor):
    subcategory = "model"
    pattern = BASE_PATTERN + r"/m/([a-z0-9]{7})"
    example = "https://en.girlygirlpic.com/m/MODELID"

    def items(self):
        self.payload["model_id"] = self.groups[1]
        yield from self._pagination("getmodelalbumslist")


class GirlygirlpicStudioExtractor(GirlygirlpicExtractor):
    subcategory = "studio"
    pattern = BASE_PATTERN + r"/c/([a-z0-9]{7})"
    example = "https://en.girlygirlpic.com/c/STUDIOID"

    def items(self):
        self.payload["company_id"] = self.groups[1]
        yield from self._pagination("getcompanyalbumslist")


class GirlygirlpicTagExtractor(GirlygirlpicExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/t/([a-z0-9]{7})"
    example = "https://en.girlygirlpic.com/t/TAGID"

    def items(self):
        self.payload["tag_id"] = self.groups[1]
        yield from self._pagination("gettagalbumslist")


class GirlygirlpicRegionExtractor(GirlygirlpicExtractor):
    subcategory = "region"
    pattern = BASE_PATTERN + r"/l/([a-z0-9]{7})"
    example = "https://en.girlygirlpic.com/l/REGIONID"

    def items(self):
        self.payload["country_id"] = self.groups[1]
        yield from self._pagination("getcountryalbumslist")


class GirlygirlpicSearchExtractor(GirlygirlpicExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/s/(.+)"
    example = "https://en.girlygirlpic.com/s/SEARCH"

    def items(self):
        self.payload["search_keys_tag"] = self.groups[1]
        yield from self._pagination("getsearchalbumslist")
