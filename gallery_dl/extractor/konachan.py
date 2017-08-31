# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://konachan.com/"""

from . import booru


class KonachanExtractor(booru.JSONBooruExtractor):
    """Base class for konachan extractors"""
    category = "konachan"
    api_url = "https://konachan.com/post.json"


class KonachanTagExtractor(KonachanExtractor, booru.BooruTagExtractor):
    """Extractor for images from konachan.com based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/post\?tags=([^&]+)"]
    test = [("http://konachan.com/post?tags=patata", {
        "content": "838cfb815e31f48160855435655ddf7bfc4ecb8d",
    })]


class KonachanPoolExtractor(KonachanExtractor, booru.BooruPoolExtractor):
    """Extractor for image-pools from konachan.com"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/pool/show/(\d+)"]
    test = [("http://konachan.com/pool/show/95", {
        "content": "cf0546e38a93c2c510a478f8744e60687b7a8426",
    })]


class KonachanPostExtractor(KonachanExtractor, booru.BooruPostExtractor):
    """Extractor for single images from konachan.com"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/post/show/(\d+)"]
    test = [("http://konachan.com/post/show/205189", {
        "content": "674e75a753df82f5ad80803f575818b8e46e4b65",
    })]


class KonachanPopularExtractor(KonachanExtractor, booru.BooruPopularExtractor):
    """Extractor for popular images from konachan.com"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/post/popular_"
               r"(by_(?:day|week|month)|recent)(?:\?([^#]*))?"]
    test = [("https://konachan.com/post/popular_by_month?month=11&year=2010", {
        "count": 20,
    })]

    @property
    def api_url(self):
        return "https://konachan.com/post/popular_" + self.scale + ".json"
