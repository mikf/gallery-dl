# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://girlgirlgo.org"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?([a-z]{2})\.girlgirlgo\.org"


class GirlgirlgoExtractor(Extractor):
    category = "girlgirlgo"
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
        url = f"https://{self.groups[0]}.girlgirlgo.org/api/{endpoint}"
        data = {"_extractor": GirlgirlgoAlbumExtractor}
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


class GirlgirlgoAlbumExtractor(GirlgirlgoExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a/([a-zA-Z0-9]+)"
    example = "https://en.girlgirlgo.org/a/ALBUM"

    def items(self):
        url = f"https://{self.groups[0]}.girlgirlgo.org/ax"
        payload = {"album_id": self.groups[1]}
        page = self.request(url, method="POST", json=payload).text
        date = text.extr(page, "datetime=", ">")
        urls = list(text.extract_iter(page, "link-w><a href=", " class"))
        data = {
            "title": text.extr(page, "<li><span>", "</span>"),
            "model": text.extr(page, "rel=author>", "</a>"),
            "tags": list(text.extract_iter(page, 'tag">', "</a>")),
            "date": text.parse_datetime(date, "%Y-%m-%dT%H:%M:%S"),
            "count": len(urls)
        }

        yield Message.Directory, data
        for data["num"], image in enumerate(urls, 1):
            text.nameext_from_url(image, data)
            yield Message.Url, image, data


class GirlgirlgoModelExtractor(GirlgirlgoExtractor):
    subcategory = "model"
    pattern = BASE_PATTERN + r"/m/([a-z0-9]{7})"
    example = "https://en.girlgirlgo.org/m/abc1234"

    def items(self):
        self.payload["model_id"] = self.groups[1]
        yield from self._pagination("getmodelalbumslist")


class GirlgirlgoStudioExtractor(GirlgirlgoExtractor):
    subcategory = "studio"
    pattern = BASE_PATTERN + r"/c/([a-z0-9]{7})"
    example = "https://en.girlgirlgo.org/c/abc1234"

    def items(self):
        self.payload["company_id"] = self.groups[1]
        yield from self._pagination("getcompanyalbumslist")


class GirlgirlgoTagExtractor(GirlgirlgoExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/t/([a-z0-9]{7})"
    example = "https://en.girlgirlgo.org/t/TAG"

    def items(self):
        self.payload["tag_id"] = self.groups[1]
        yield from self._pagination("gettagalbumslist")


class GirlgirlgoRegionExtractor(GirlgirlgoExtractor):
    subcategory = "region"
    pattern = BASE_PATTERN + r"/l/([a-z0-9]{7})"
    example = "https://en.girlgirlgo.org/l/abc1234"

    def items(self):
        self.payload["country_id"] = self.groups[1]
        yield from self._pagination("getcountryalbumslist")


class GirlgirlgoSearchExtractor(GirlgirlgoExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/s/(.+)"
    example = "https://en.girlgirlgo.org/s/SEARCH"

    def items(self):
        self.payload["search_keys_tag"] = self.groups[1]
        yield from self._pagination("getsearchalbumslist")
