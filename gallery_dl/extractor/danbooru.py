# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://danbooru.donmai.us/"""

from . import booru


BASE_PATTERN = (
    r"(?:https?://)?"
    r"(?P<subdomain>danbooru|hijiribe|sonohara|safebooru)"
    r"\.donmai\.us")


class DanbooruExtractor(booru.DanbooruPageMixin, booru.BooruExtractor):
    """Base class for danbooru extractors"""
    category = "danbooru"
    page_limit = 1000

    def __init__(self, match):
        super().__init__(match)
        self.subdomain = match.group("subdomain")
        self.scheme = "https" if self.subdomain == "danbooru" else "http"
        self.api_url = "{scheme}://{subdomain}.donmai.us/posts.json".format(
            scheme=self.scheme, subdomain=self.subdomain)


class DanbooruTagExtractor(booru.TagMixin, DanbooruExtractor):
    """Extractor for images from danbooru based on search-tags"""
    pattern = [BASE_PATTERN + r"/posts\?(?:[^&#]*&)*tags=(?P<tags>[^&#]+)"]
    test = [
        ("https://danbooru.donmai.us/posts?tags=bonocho", {
            "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
        }),
        # test page transitions
        ("https://danbooru.donmai.us/posts?tags=canvas_%28cocktail_soft%29", {
            "count": ">= 50",
        }),
        ("https://hijiribe.donmai.us/posts?tags=bonocho", None),
        ("https://sonohara.donmai.us/posts?tags=bonocho", None),
        ("https://safebooru.donmai.us/posts?tags=bonocho", None),
    ]


class DanbooruPoolExtractor(booru.PoolMixin, DanbooruExtractor):
    """Extractor for image-pools from danbooru"""
    pattern = [BASE_PATTERN + r"/pools/(?P<pool>\d+)"]
    test = [("https://danbooru.donmai.us/pools/7659", {
        "content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
    })]


class DanbooruPostExtractor(booru.PostMixin, DanbooruExtractor):
    """Extractor for single images from danbooru"""
    pattern = [BASE_PATTERN + r"/posts/(?P<post>\d+)"]
    test = [("https://danbooru.donmai.us/posts/294929", {
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
    })]


class DanbooruPopularExtractor(booru.PopularMixin, DanbooruExtractor):
    """Extractor for popular images from danbooru"""
    pattern = [BASE_PATTERN + r"/explore/posts/popular(?:\?(?P<query>[^#]*))?"]
    test = [
        ("https://danbooru.donmai.us/explore/posts/popular", None),
        (("https://danbooru.donmai.us/explore/posts/popular"
          "?date=2013-06-06+03%3A34%3A22+-0400&scale=week"), {
            "count": ">= 1",
        }),
    ]

    def __init__(self, match):
        super().__init__(match)
        urlfmt = "{scheme}://{subdomain}.donmai.us/explore/posts/popular.json"
        self.api_url = urlfmt.format(
            scheme=self.scheme, subdomain=self.subdomain)
