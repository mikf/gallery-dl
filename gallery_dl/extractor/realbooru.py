# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://realbooru.com/"""

from . import booru


class RealbooruExtractor(booru.XmlParserMixin,
                         booru.GelbooruPageMixin,
                         booru.BooruExtractor):
    """Base class for realbooru extractors"""
    category = "realbooru"
    api_url = "https://realbooru.com/index.php"
    post_url = "https://realbooru.com/index.php?page=post&s=view&id={}"
    pool_url = "https://realbooru.com/index.php?page=pool&s=show&id={}"

    def __init__(self, match):
        super().__init__(match)
        self.params.update({"page": "dapi", "s": "post", "q": "index"})


class RealbooruTagExtractor(booru.TagMixin, RealbooruExtractor):
    """Extractor for images from realbooru.com based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?realbooru\.com/(?:index\.php)?"
               r"\?page=post&s=list&tags=(?P<tags>[^&#]+)")
    test = ("https://realbooru.com/index.php?page=post&s=list&tags=wine", {
        "count": ">= 64",
    })


class RealbooruPoolExtractor(booru.GelbooruPoolMixin, RealbooruExtractor):
    """Extractor for image-pools from realbooru.com"""
    pattern = (r"(?:https?://)?(?:www\.)?realbooru\.com/(?:index\.php)?"
               r"\?page=pool&s=show&id=(?P<pool>\d+)")
    test = ("https://realbooru.com/index.php?page=pool&s=show&id=1", {
        "count": 3,
    })


class RealbooruPostExtractor(booru.PostMixin, RealbooruExtractor):
    """Extractor for single images from realbooru.com"""
    pattern = (r"(?:https?://)?(?:www\.)?realbooru\.com/(?:index\.php)?"
               r"\?page=post&s=view&id=(?P<post>\d+)")
    test = ("https://realbooru.com/index.php?page=post&s=view&id=668483", {
        "url": "2421b5b0e15d5e20f9067090a8b0fd4114d3e7d9",
        "content": "7f5873ce3b6cd295ea2e81fcb49583098ea9c8da",
        #  "options": (("tags", True),),
        #  "keyword": {
        #      "tags_general" : str,
        #      "tags_metadata": str,
        #      "tags_model"   : "jennifer_lawrence",
        #  },
    })
