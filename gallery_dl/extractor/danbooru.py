# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://danbooru.donmai.us/"""

from . import booru


class DanbooruExtractor(booru.JSONBooruExtractor):
    """Base class for danbooru extractors"""
    category = "danbooru"
    api_url = "https://danbooru.donmai.us/posts.json"


class DanbooruTagExtractor(DanbooruExtractor, booru.BooruTagExtractor):
    """Extractor for images from danbooru based on search-tags"""
    pattern = [r"(?:https?://)?(?:danbooru|hijiribe|sonohara)\.donmai\.us"
               r"/posts\?(?:[^&#]*&)*tags=([^&#]+)"]
    test = [
        ("https://danbooru.donmai.us/posts?tags=bonocho", {
            "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
        }),
        ("https://hijiribe.donmai.us/posts?tags=bonocho", None),
        ("https://sonohara.donmai.us/posts?tags=bonocho", None),
    ]


class DanbooruPoolExtractor(DanbooruExtractor, booru.BooruPoolExtractor):
    """Extractor for image-pools from danbooru"""
    pattern = [r"(?:https?://)?(?:danbooru|hijiribe|sonohara)\.donmai\.us"
               r"/pools/(\d+)"]
    test = [("https://danbooru.donmai.us/pools/7659", {
        "content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
    })]


class DanbooruPostExtractor(DanbooruExtractor, booru.BooruPostExtractor):
    """Extractor for single images from danbooru"""
    pattern = [r"(?:https?://)?(?:danbooru|hijiribe|sonohara)\.donmai\.us"
               r"/posts/(\d+)"]
    test = [("https://danbooru.donmai.us/posts/294929", {
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
    })]


class DanbooruPopularExtractor(DanbooruExtractor, booru.BooruPopularExtractor):
    """Extractor for popular images from danbooru"""
    pattern = [r"(?:https?://)?(?:danbooru|hijiribe|sonohara)\.donmai\.us"
               r"/explore/posts/popular()(?:\?([^#]*))?"]
    test = [
        ("https://danbooru.donmai.us/explore/posts/popular", None),
        (("https://danbooru.donmai.us/explore/posts/popular"
          "?date=2013-06-06+03%3A34%3A22+-0400&scale=week"), {
            "count": 20,
        }),
    ]
    api_url = "https://danbooru.donmai.us/explore/posts/popular.json"
