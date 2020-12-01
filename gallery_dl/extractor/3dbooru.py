# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://behoimi.org/"""

from . import moebooru


class _3dbooruBase():
    """Base class for 3dbooru extractors"""
    category = "3dbooru"
    basecategory = "booru"
    root = "http://behoimi.org"

    def __init__(self, match):
        super().__init__(match)
        self.session.headers.update({
            "Referer": "http://behoimi.org/post/show/",
            "Accept-Encoding": "identity",
        })


class _3dbooruTagExtractor(_3dbooruBase, moebooru.MoebooruTagExtractor):
    """Extractor for images from behoimi.org based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?behoimi\.org/post"
               r"(?:/(?:index)?)?\?tags=(?P<tags>[^&#]+)")
    test = ("http://behoimi.org/post?tags=himekawa_azuru+dress", {
        "url": "ecb30c6aaaf8a6ff8f55255737a9840832a483c1",
        "content": "11cbda40c287e026c1ce4ca430810f761f2d0b2a",
    })

    def posts(self):
        params = {"tags": self.tags}
        return self._pagination(self.root + "/post/index.json", params)


class _3dbooruPoolExtractor(_3dbooruBase, moebooru.MoebooruPoolExtractor):
    """Extractor for image-pools from behoimi.org"""
    pattern = r"(?:https?://)?(?:www\.)?behoimi\.org/pool/show/(?P<pool>\d+)"
    test = ("http://behoimi.org/pool/show/27", {
        "url": "da75d2d1475449d5ef0c266cb612683b110a30f2",
        "content": "fd5b37c5c6c2de4b4d6f1facffdefa1e28176554",
    })

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination(self.root + "/post/index.json", params)


class _3dbooruPostExtractor(_3dbooruBase, moebooru.MoebooruPostExtractor):
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

    def posts(self):
        params = {"tags": "id:" + self.post_id}
        return self._pagination(self.root + "/post/index.json", params)


class _3dbooruPopularExtractor(
        _3dbooruBase, moebooru.MoebooruPopularExtractor):
    """Extractor for popular images from behoimi.org"""
    pattern = (r"(?:https?://)?(?:www\.)?behoimi\.org"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?")
    test = ("http://behoimi.org/post/popular_by_month?month=2&year=2013", {
        "pattern": r"http://behoimi\.org/data/../../[0-9a-f]{32}\.jpg",
        "count": 20,
    })
