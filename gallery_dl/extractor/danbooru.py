# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://danbooru.donmai.us/"""

from . import booru

class DanbooruExtractor(booru.JSONBooruExtractor):
    """Base class for danbooru extractors"""
    category = "danbooru"
    api_url = "https://danbooru.donmai.us/posts.json"

class DanbooruTagExtractor(DanbooruExtractor, booru.BooruTagExtractor):
    """Extract images from danbooru based on search-tags"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts\?(?:utf8=%E2%9C%93&)?tags=([^&]+)"]
    test = [("https://danbooru.donmai.us/posts?tags=heath_ledger", {
        "url": "a261c33f117c7395f0eac54091075e67c8e66fca",
        "keyword": "fc4685c98aedaf2383384d47af4f7bd257c40f32",
    })]

class DanbooruPoolExtractor(DanbooruExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from danbooru"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/pools/(\d+)"]
    test = [("https://danbooru.donmai.us/pools/7659", {
        "url": "db522c7f74d42ec1940fb23d1a58ed8edb65f9ae",
        "keyword": "bf8256e88ac0d032808e9f5aa165c9a1fa7e451c",
    })]

class DanbooruPostExtractor(DanbooruExtractor, booru.BooruPostExtractor):
    """Extract single images from danbooru"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts/(\d+)"]
    test = [("https://danbooru.donmai.us/posts/1534703", {
        "url": "3a87a761dad69dfa038499aeacef679a3912816b",
        "keyword": "0a2f4dd6b8384fcbc805302040234536895a2dc3",
    })]
