# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from http://behoimi.org/"""

from . import booru

class ThreeDeeBooruExtractor(booru.JSONBooruExtractor):
    """Base class for 3dbooru extractors"""
    category = "3dbooru"
    api_url = "http://behoimi.org/post/index.json"
    headers = {
        "Referer": "http://behoimi.org/post/show/",
        "User-Agent": "Mozilla/5.0",
    }

class ThreeDeeBooruTagExtractor(ThreeDeeBooruExtractor, booru.BooruTagExtractor):
    """Extract images from 3dbooru based on search-tags"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/post(?:/(?:index)?)?\?tags=([^&]+)"]
    test = [("http://behoimi.org/post/index?tags=himekawa_azuru", {
        "url": "6f6f485fb92629bc22a5df18b7cbb3ac13ae46b2",
        "keyword": "df2f7b1fb0efb739eed55788de700a1b834d2896",
    })]

class ThreeDeeBooruPoolExtractor(ThreeDeeBooruExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from 3dbooru"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/pool/show/(\d+)"]
    test = [("http://behoimi.org/pool/show/27", {
        "url": "da75d2d1475449d5ef0c266cb612683b110a30f2",
        "keyword": "ea76fd6cef4430bee403d080bf173af829a4390a",
    })]

class ThreeDeeBooruPostExtractor(ThreeDeeBooruExtractor, booru.BooruPostExtractor):
    """Extract single images from 3dbooru"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/post/show/(\d+)"]
    test = [("http://behoimi.org/post/show/140852", {
        "url": "ce874ea26f01d6c94795f3cc3aaaaa9bc325f2f6",
        "keyword": "ebde54ed04e1de7d1fd819728963f754b77a693e",
    })]
