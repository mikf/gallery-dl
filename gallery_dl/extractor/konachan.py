# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://konachan.com/"""

from . import booru

class KonachanExtractor(booru.JSONBooruExtractor):
    """Base class for konachan extractors"""
    category = "konachan"
    api_url = "https://konachan.com/post.json"

class KonachanTagExtractor(KonachanExtractor, booru.BooruTagExtractor):
    """Extract images from konachan based on search-tags"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/post\?tags=([^&]+)"]
    test = [("http://konachan.com/post?tags=batman_(series)", {
        "url": "3bc7d258f74854002028ae861f2977835a022454",
        "keyword": "e5c5767a0d3968be5465b1d00817467bf9fac1b1",
    })]

class KonachanPoolExtractor(KonachanExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from konachan"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/pool/show/(\d+)"]
    test = [("http://konachan.com/pool/show/5", {
        "url": "27f0b7bc60bb8961612005b53c8d46cf76272003",
        "keyword": "9d1eba1c4adbf751f4b5dac2f79eb4dbec1ca577",
    })]

class KonachanPostExtractor(KonachanExtractor, booru.BooruPostExtractor):
    """Extract single images from konachan"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/post/show/(\d+)"]
    test = [("http://konachan.com/post/show/141341", {
        "url": "3bc7d258f74854002028ae861f2977835a022454",
        "keyword": "df1ce9be720e335f68eca1a53d3df6cf727b6372",
    })]
