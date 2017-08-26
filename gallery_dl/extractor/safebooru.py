# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://safebooru.org/"""

from . import booru


class SafebooruExtractor(booru.XMLBooruExtractor):
    """Base class for safebooru extractors"""
    category = "safebooru"
    api_url = "https://safebooru.org/index.php"
    pagestart = 0
    pagekey = "pid"

    def setup(self):
        self.params.update({"page": "dapi", "s": "post", "q": "index"})


class SafebooruTagExtractor(SafebooruExtractor, booru.BooruTagExtractor):
    """Extractor for images from safebooru.org based on search-tags"""
    pattern = [(r"(?:https?://)?(?:www\.)?safebooru\.org/(?:index\.php)?"
                r"\?page=post&s=list&tags=([^&]+)")]
    test = [("http://safebooru.org/index.php?page=post&s=list&tags=bonocho", {
        "url": "17c61b386530cf4c30842c9f580d15ef1cd09586",
        "content": "e5ad4c5bf241b1def154958535bef6c2f6b733eb",
    })]


class SafebooruPostExtractor(SafebooruExtractor, booru.BooruPostExtractor):
    """Extractor for single images from safebooru.org"""
    pattern = [(r"(?:https?://)?(?:www\.)?safebooru\.org/(?:index\.php)?"
                r"\?page=post&s=view&id=(\d+)")]
    test = [("http://safebooru.org/index.php?page=post&s=view&id=1169132", {
        "url": "cf05e37a3c62b2d55788e2080b8eabedb00f999b",
        "content": "93b293b27dabd198afafabbaf87c49863ac82f27",
    })]
