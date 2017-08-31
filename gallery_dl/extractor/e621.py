# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://e621.net/"""

from . import booru


class E621Extractor(booru.JSONBooruExtractor):
    """Base class for e621 extractors"""
    category = "e621"
    api_url = "https://e621.net/post/index.json"


class E621TagExtractor(E621Extractor, booru.BooruTagExtractor):
    """Extractor for images from e621.net based on search-tags"""
    pattern = [
        r"(?:https?://)?(?:www\.)?e621\.net/post/index/\d+/([^?]+)",
        r"(?:https?://)?(?:www\.)?e621\.net/post\?tags=([^&]+)",
    ]
    test = [("https://e621.net/post/index/1/anry", {
        "url": "8021e5ea28d47c474c1ffc9bd44863c4d45700ba",
        "content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
    })]


class E621PoolExtractor(E621Extractor, booru.BooruPoolExtractor):
    """Extractor for image-pools from e621.net"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net/pool/show/(\d+)"]
    test = [("https://e621.net/pool/show/73", {
        "url": "842f2fb065c7c339486a9b1d689020b8569888ed",
        "content": "c2c87b7a9150509496cddc75ccab08109922876a",
    })]


class E621PostExtractor(E621Extractor, booru.BooruPostExtractor):
    """Extractor for single images from e621.net"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net/post/show/(\d+)"]
    test = [("https://e621.net/post/show/535", {
        "url": "f7f78b44c9b88f8f09caac080adc8d6d9fdaa529",
        "content": "66f46e96a893fba8e694c4e049b23c2acc9af462",
    })]


class E621PopularExtractor(E621Extractor, booru.BooruPopularExtractor):
    """Extractor for popular images from 621.net"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net/post/popular_by_"
               r"(day|week|month)(?:\?([^#]*))?"]
    test = [("https://e621.net/post/popular_by_month?month=6&year=2013", {
        "count": 32,
    })]

    @property
    def api_url(self):
        return "https://e621.net/post/popular_by_" + self.scale + ".json"
