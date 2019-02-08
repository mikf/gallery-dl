# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://konachan.com/"""

from . import booru


class KonachanExtractor(booru.MoebooruPageMixin, booru.BooruExtractor):
    """Base class for konachan extractors"""
    category = "konachan"

    def __init__(self, match):
        root = "https://konachan." + match.group("tld")
        self.api_url = root + "/post.json"
        self.post_url = root + "/post/show/{}"
        super().__init__(match)


class KonachanTagExtractor(booru.TagMixin, KonachanExtractor):
    """Extractor for images from konachan.com based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/post\?(?:[^&#]*&)*tags=(?P<tags>[^&#]+)")
    test = (
        ("https://konachan.com/post?tags=patata", {
            "content": "838cfb815e31f48160855435655ddf7bfc4ecb8d",
        }),
        ("https://konachan.net/post?tags=patata"),
    )


class KonachanPoolExtractor(booru.PoolMixin, KonachanExtractor):
    """Extractor for image-pools from konachan.com"""
    pattern = (r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/pool/show/(?P<pool>\d+)")
    test = (
        ("https://konachan.com/pool/show/95", {
            "content": "cf0546e38a93c2c510a478f8744e60687b7a8426",
        }),
        ("https://konachan.net/pool/show/95"),
    )


class KonachanPostExtractor(booru.PostMixin, KonachanExtractor):
    """Extractor for single images from konachan.com"""
    pattern = (r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/post/show/(?P<post>\d+)")
    test = (
        ("https://konachan.com/post/show/205189", {
            "content": "674e75a753df82f5ad80803f575818b8e46e4b65",
            "options": (("tags", True),),
            "keyword": {
                "tags_artist": "patata",
                "tags_character": "clownpiece",
                "tags_copyright": "touhou",
                "tags_general": str,
            },
        }),
        ("https://konachan.net/post/show/205189"),
    )


class KonachanPopularExtractor(booru.MoebooruPopularMixin, KonachanExtractor):
    """Extractor for popular images from konachan.com"""
    pattern = (r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?")
    test = (
        ("https://konachan.com/post/popular_by_month?month=11&year=2010", {
            "count": 20,
        }),
        ("https://konachan.com/post/popular_recent"),
        ("https://konachan.net/post/popular_recent"),
    )

    def __init__(self, match):
        super().__init__(match)
        self.api_url = (
            "https://konachan.{tld}/post/popular_{scale}.json".format(
                tld=match.group("tld"), scale=self.scale))
