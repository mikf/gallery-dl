# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hypnohub.net/"""

from . import booru


class HypnohubExtractor(booru.MoebooruPageMixin, booru.BooruExtractor):
    """Base class for hypnohub extractors"""
    category = "hypnohub"
    api_url = "https://hypnohub.net/post.json"
    post_url = "https://hypnohub.net/post/show/{}"


class HypnohubTagExtractor(booru.TagMixin, HypnohubExtractor):
    """Extractor for images from hypnohub.net based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?hypnohub\.net"
               r"/post\?(?:[^&#]*&)*tags=(?P<tags>[^&#]+)")
    test = ("https://hypnohub.net/post?tags=gonoike_biwa", {
        "url": "2848abe3e433ad39bfdf5be5874682faaccea5be",
    })


class HypnohubPoolExtractor(booru.PoolMixin, HypnohubExtractor):
    """Extractor for image-pools from hypnohub.net"""
    pattern = r"(?:https?://)?(?:www\.)?hypnohub\.net/pool/show/(?P<pool>\d+)"
    test = ("https://hypnohub.net/pool/show/61", {
        "url": "fd74991c8729e77acd3c35eb6ddc4128ff445adf",
    })


class HypnohubPostExtractor(booru.PostMixin, HypnohubExtractor):
    """Extractor for single images from hypnohub.net"""
    pattern = r"(?:https?://)?(?:www\.)?hypnohub\.net/post/show/(?P<post>\d+)"
    test = ("https://hypnohub.net/post/show/73964", {
        "content": "02d5f5a8396b621a6efc04c5f8ef1b7225dfc6ee",
        "options": (("tags", True),),
        "keyword": {
            "tags_artist": "gonoike_biwa icontrol_(manipper)",
            "tags_character": "komaru_naegi",
            "tags_copyright": "dangan_ronpa dangan_ronpa_another_episode",
            "tags_general": str,
        },
    })


class HypnohubPopularExtractor(booru.MoebooruPopularMixin, HypnohubExtractor):
    """Extractor for popular images from hypnohub.net"""
    pattern = (r"(?:https?://)?(?:www\.)?hypnohub\.net"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?")
    test = (
        ("https://hypnohub.net/post/popular_by_month?month=6&year=2014", {
            "count": 20,
        }),
        ("https://hypnohub.net/post/popular_recent"),
    )

    def __init__(self, match):
        super().__init__(match)
        self.api_url = "https://hypnohub.net/post/popular_{scale}.json".format(
            scale=self.scale)
