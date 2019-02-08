# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://yande.re/"""

from . import booru


class YandereExtractor(booru.MoebooruPageMixin, booru.BooruExtractor):
    """Base class for yandere extractors"""
    category = "yandere"
    api_url = "https://yande.re/post.json"
    post_url = "https://yande.re/post/show/{}"


class YandereTagExtractor(booru.TagMixin, YandereExtractor):
    """Extractor for images from yande.re based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?yande\.re"
               r"/post\?(?:[^&#]*&)*tags=(?P<tags>[^&#]+)")
    test = ("https://yande.re/post?tags=ouzoku+armor", {
        "content": "59201811c728096b2d95ce6896fd0009235fe683",
    })


class YanderePoolExtractor(booru.PoolMixin, YandereExtractor):
    """Extractor for image-pools from yande.re"""
    pattern = r"(?:https?://)?(?:www\.)?yande\.re/pool/show/(?P<pool>\d+)"
    test = ("https://yande.re/pool/show/318", {
        "content": "2a35b9d6edecce11cc2918c6dce4de2198342b68",
    })


class YanderePostExtractor(booru.PostMixin, YandereExtractor):
    """Extractor for single images from yande.re"""
    pattern = r"(?:https?://)?(?:www\.)?yande\.re/post/show/(?P<post>\d+)"
    test = ("https://yande.re/post/show/51824", {
        "content": "59201811c728096b2d95ce6896fd0009235fe683",
        "options": (("tags", True),),
        "keyword": {
            "tags_artist": "sasaki_tamaru",
            "tags_circle": "softhouse_chara",
            "tags_copyright": "ouzoku",
            "tags_general": str,
        },
    })


class YanderePopularExtractor(booru.MoebooruPopularMixin, YandereExtractor):
    """Extractor for popular images from yande.re"""
    pattern = (r"(?:https?://)?(?:www\.)?yande\.re"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?")
    test = (
        ("https://yande.re/post/popular_by_month?month=6&year=2014", {
            "count": 40,
        }),
        ("https://yande.re/post/popular_recent"),
    )

    def __init__(self, match):
        super().__init__(match)
        self.api_url = "https://yande.re/post/popular_{scale}.json".format(
            scale=self.scale)
