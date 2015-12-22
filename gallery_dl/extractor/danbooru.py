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
    pattern = [(r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts"
                r"\?(?:utf8=%E2%9C%93&)?tags=([^&]+)")]
    test = [("https://danbooru.donmai.us/posts?tags=bonocho", {
        "url": "f05b24cfd01a98eab6e8a4501885e3c29928738c",
        "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
    })]

class DanbooruPoolExtractor(DanbooruExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from danbooru"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/pools/(\d+)"]
    test = [("https://danbooru.donmai.us/pools/7659", {
        "url": "db522c7f74d42ec1940fb23d1a58ed8edb65f9ae",
        "content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
    })]

class DanbooruPostExtractor(DanbooruExtractor, booru.BooruPostExtractor):
    """Extract single images from danbooru"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts/(\d+)"]
    test = [("https://danbooru.donmai.us/posts/294929", {
        "url": "98fb9f9dc48ef5794891c6725f3610efaf6042c1",
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
    })]
