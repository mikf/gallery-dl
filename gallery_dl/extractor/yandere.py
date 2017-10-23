# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://yande.re/"""

from . import booru


class YandereExtractor(booru.JSONBooruExtractor):
    """Base class for yandere extractors"""
    category = "yandere"
    api_url = "https://yande.re/post.json"


class YandereTagExtractor(YandereExtractor, booru.BooruTagExtractor):
    """Extractor for images from yande.re based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re/post\?tags=([^&]+)"]
    test = [("https://yande.re/post?tags=ouzoku+armor", {
        "content": "59201811c728096b2d95ce6896fd0009235fe683",
    })]


class YanderePoolExtractor(YandereExtractor, booru.BooruPoolExtractor):
    """Extractor for image-pools from yande.re"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re/pool/show/(\d+)"]
    test = [("https://yande.re/pool/show/318", {
        "content": "2a35b9d6edecce11cc2918c6dce4de2198342b68",
    })]


class YanderePostExtractor(YandereExtractor, booru.BooruPostExtractor):
    """Extractor for single images from yande.re"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re/post/show/(\d+)"]
    test = [("https://yande.re/post/show/51824", {
        "content": "59201811c728096b2d95ce6896fd0009235fe683",
    })]


class YanderePopularExtractor(YandereExtractor, booru.BooruPopularExtractor):
    """Extractor for popular images from yande.re"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re/post/popular_"
               r"(by_(?:day|week|month)|recent)(?:\?([^#]*))?"]
    test = [
        ("https://yande.re/post/popular_by_month?month=6&year=2014", {
            "count": 40,
        }),
        ("https://yande.re/post/popular_recent", None),
    ]

    @property
    def api_url(self):
        return "https://yande.re/post/popular_" + self.scale + ".json"
