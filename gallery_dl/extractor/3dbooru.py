# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://behoimi.org/"""

from . import booru


class _3dbooruExtractor(booru.MoebooruPageMixin, booru.BooruExtractor):
    """Base class for 3dbooru extractors"""
    category = "3dbooru"
    api_url = "http://behoimi.org/post/index.json"
    post_url = "http://behoimi.org/post/show/{}"
    page_limit = 1000

    def __init__(self, match):
        super().__init__(match)
        self.session.headers.update({
            "Referer": "http://behoimi.org/post/show/",
            "Accept-Encoding": "identity",
        })


class _3dbooruTagExtractor(booru.TagMixin, _3dbooruExtractor):
    """Extractor for images from behoimi.org based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?behoimi\.org/post"
               r"(?:/(?:index)?)?\?tags=(?P<tags>[^&#]+)")
    test = ("http://behoimi.org/post?tags=himekawa_azuru+dress", {
        "url": "ecb30c6aaaf8a6ff8f55255737a9840832a483c1",
        "content": "11cbda40c287e026c1ce4ca430810f761f2d0b2a",
    })


class _3dbooruPoolExtractor(booru.PoolMixin, _3dbooruExtractor):
    """Extractor for image-pools from behoimi.org"""
    pattern = r"(?:https?://)?(?:www\.)?behoimi\.org/pool/show/(?P<pool>\d+)"
    test = ("http://behoimi.org/pool/show/27", {
        "url": "da75d2d1475449d5ef0c266cb612683b110a30f2",
        "content": "fd5b37c5c6c2de4b4d6f1facffdefa1e28176554",
    })


class _3dbooruPostExtractor(booru.PostMixin, _3dbooruExtractor):
    """Extractor for single images from behoimi.org"""
    pattern = r"(?:https?://)?(?:www\.)?behoimi\.org/post/show/(?P<post>\d+)"
    test = ("http://behoimi.org/post/show/140852", {
        "url": "ce874ea26f01d6c94795f3cc3aaaaa9bc325f2f6",
        "content": "26549d55b82aa9a6c1686b96af8bfcfa50805cd4",
        "options": (("tags", True),),
        "keyword": {
            "tags_character": "furude_rika",
            "tags_copyright": "higurashi_no_naku_koro_ni",
            "tags_model": "himekawa_azuru",
            "tags_general": str,
        },
    })


class _3dbooruPopularExtractor(booru.MoebooruPopularMixin, _3dbooruExtractor):
    """Extractor for popular images from behoimi.org"""
    pattern = (r"(?:https?://)?(?:www\.)?behoimi\.org"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?")
    test = ("http://behoimi.org/post/popular_by_month?month=2&year=2013", {
        "pattern": r"http://behoimi\.org/data/../../[0-9a-f]{32}\.jpg",
        "count": 20,
    })

    def __init__(self, match):
        super().__init__(match)
        self.api_url = "http://behoimi.org/post/popular_{scale}.json".format(
            scale=self.scale)
