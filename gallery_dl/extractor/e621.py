# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://e621.net/"""

from . import booru


class E621Extractor(booru.MoebooruPageMixin, booru.BooruExtractor):
    """Base class for e621 extractors"""
    category = "e621"
    api_url = "https://e621.net/post/index.json"
    post_url = "https://e621.net/post/show/{}"
    page_limit = 750


class E621TagExtractor(booru.TagMixin, E621Extractor):
    """Extractor for images from e621.net based on search-tags"""
    pattern = [
        r"(?:https?://)?(?:www\.)?e621\.net/post/index/\d+/(?P<tags>[^/?&#]+)",
        r"(?:https?://)?(?:www\.)?e621\.net/post\?tags=(?P<tags>[^&#]+)",
    ]
    test = [
        ("https://e621.net/post/index/1/anry", {
            "url": "8021e5ea28d47c474c1ffc9bd44863c4d45700ba",
            "content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
        }),
        ("https://e621.net/post?tags=anry", None),
    ]


class E621PoolExtractor(booru.PoolMixin, E621Extractor):
    """Extractor for image-pools from e621.net"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net/pool/show/(?P<pool>\d+)"]
    test = [("https://e621.net/pool/show/73", {
        "url": "842f2fb065c7c339486a9b1d689020b8569888ed",
        "content": "c2c87b7a9150509496cddc75ccab08109922876a",
    })]


class E621PostExtractor(booru.PostMixin, E621Extractor):
    """Extractor for single images from e621.net"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net/post/show/(?P<post>\d+)"]
    test = [("https://e621.net/post/show/535", {
        "url": "f7f78b44c9b88f8f09caac080adc8d6d9fdaa529",
        "content": "66f46e96a893fba8e694c4e049b23c2acc9af462",
        "options": (("tags", True),),
        "keyword": {
            "tags_artist": "anry",
            "tags_general": str,
            "tags_species": str,
        },
    })]


class E621PopularExtractor(booru.MoebooruPopularMixin, E621Extractor):
    """Extractor for popular images from 621.net"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net"
               r"/post/popular_by_(?P<scale>day|week|month)"
               r"(?:\?(?P<query>[^#]*))?"]
    test = [("https://e621.net/post/popular_by_month?month=6&year=2013", {
        "count": 32,
    })]

    def __init__(self, match):
        super().__init__(match)
        self.api_url = "https://e621.net/post/popular_by_{scale}.json".format(
            scale=self.scale)
