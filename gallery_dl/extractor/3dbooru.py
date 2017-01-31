# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://behoimi.org/"""

from . import booru


class ThreedeebooruExtractor(booru.JSONBooruExtractor):
    """Base class for 3dbooru extractors"""
    category = "3dbooru"
    api_url = "http://behoimi.org/post/index.json"
    headers = {
        "Referer": "http://behoimi.org/post/show/",
        "User-Agent": "Mozilla/5.0",
    }


class ThreedeebooruTagExtractor(ThreedeebooruExtractor,
                                booru.BooruTagExtractor):
    """Extractor for images from behoimi.org based on search-tags"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/post"
               r"(?:/(?:index)?)?\?tags=([^&]+)"]
    test = [("http://behoimi.org/post?tags=himekawa_azuru dress", {
        "url": "ecb30c6aaaf8a6ff8f55255737a9840832a483c1",
        "content": "11cbda40c287e026c1ce4ca430810f761f2d0b2a",
    })]


class ThreedeebooruPoolExtractor(ThreedeebooruExtractor,
                                 booru.BooruPoolExtractor):
    """Extractor for image-pools from behoimi.org"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/pool/show/(\d+)"]
    test = [("http://behoimi.org/pool/show/27", {
        "url": "da75d2d1475449d5ef0c266cb612683b110a30f2",
        "content": "fd5b37c5c6c2de4b4d6f1facffdefa1e28176554",
    })]


class ThreedeebooruPostExtractor(ThreedeebooruExtractor,
                                 booru.BooruPostExtractor):
    """Extractor for single images from behoimi.org"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/post/show/(\d+)"]
    test = [("http://behoimi.org/post/show/140852", {
        "url": "ce874ea26f01d6c94795f3cc3aaaaa9bc325f2f6",
        "content": "26549d55b82aa9a6c1686b96af8bfcfa50805cd4",
    })]
