# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://yande.re/"""

from . import booru
from .. import text


class YandereExtractor(booru.MoebooruPageMixin, booru.BooruExtractor):
    """Base class for yandere extractors"""
    category = "yandere"
    api_url = "https://yande.re/post.json"

    def __init__(self, match):
        super().__init__(match)
        if self.config("tags", False):
            self.prepare = self._categorize_tags

    def _categorize_tags(self, image):
        url = "https://yande.re/post/show/{}".format(image["id"])
        page = self.request(url).text
        taghtml = text.extract(page, '<ul id="tag-sidebar">', '</ul>')[0]

        pos = 0
        tags = {"artist": [], "copyright": [], "character": [],
                "circle": [], "faults": [], "general": []}

        while True:
            tagtype, pos = text.extract(taghtml, "tag-type-", '"', pos)
            if not tagtype:
                break
            tagname, pos = text.extract(taghtml, "?tags=", '"', pos)
            tags[tagtype].append(text.unquote(tagname))

        for key, value in tags.items():
            image["tags_" + key] = " ".join(value)


class YandereTagExtractor(booru.TagMixin, YandereExtractor):
    """Extractor for images from yande.re based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re"
               r"/post\?(?:[^&#]*&)*tags=(?P<tags>[^&#]+)"]
    test = [("https://yande.re/post?tags=ouzoku+armor", {
        "content": "59201811c728096b2d95ce6896fd0009235fe683",
    })]


class YanderePoolExtractor(booru.PoolMixin, YandereExtractor):
    """Extractor for image-pools from yande.re"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re/pool/show/(?P<pool>\d+)"]
    test = [("https://yande.re/pool/show/318", {
        "content": "2a35b9d6edecce11cc2918c6dce4de2198342b68",
    })]


class YanderePostExtractor(booru.PostMixin, YandereExtractor):
    """Extractor for single images from yande.re"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re/post/show/(?P<post>\d+)"]
    test = [("https://yande.re/post/show/51824", {
        "content": "59201811c728096b2d95ce6896fd0009235fe683",
        "options": (("tags", True),),
        "keyword": {
            "tags_artist": "sasaki_tamaru",
            "tags_circle": "softhouse_chara",
            "tags_copyright": "ouzoku",
            "tags_character": str,
            "tags_faults": str,
            "tags_general": str,
        },
    })]


class YanderePopularExtractor(booru.MoebooruPopularMixin, YandereExtractor):
    """Extractor for popular images from yande.re"""
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?"]
    test = [
        ("https://yande.re/post/popular_by_month?month=6&year=2014", {
            "count": 40,
        }),
        ("https://yande.re/post/popular_recent", None),
    ]

    def __init__(self, match):
        super().__init__(match)
        self.api_url = "https://yande.re/post/popular_{scale}.json".format(
            scale=self.scale)
