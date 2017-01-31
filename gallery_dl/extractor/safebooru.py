# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://safebooru.org/"""

from . import booru


class SafebooruExtractor(booru.XMLBooruExtractor):
    """Base class for safebooru extractors"""
    category = "safebooru"
    api_url = "http://safebooru.org/index.php"

    def setup(self):
        self.params.update({"page": "dapi", "s": "post", "q": "index"})

    def update_page(self, reset=False):
        if reset is False:
            self.params["pid"] += 1
        else:
            self.params["pid"] = 0


class SafebooruTagExtractor(SafebooruExtractor, booru.BooruTagExtractor):
    """Extractor for images from safebooru.org based on search-tags"""
    subcategory = "tag"
    pattern = [(r"(?:https?://)?(?:www\.)?safebooru\.org/(?:index\.php)?"
                r"\?page=post&s=list&tags=([^&]+)")]
    test = [("http://safebooru.org/index.php?page=post&s=list&tags=bonocho", {
        "url": "c91e04ffbdf317fae95b2e160c8345503d9fb730",
        "content": "e5ad4c5bf241b1def154958535bef6c2f6b733eb",
    })]


class SafebooruPostExtractor(SafebooruExtractor, booru.BooruPostExtractor):
    """Extractor for single images from safebooru.org"""
    subcategory = "post"
    pattern = [(r"(?:https?://)?(?:www\.)?safebooru\.org/(?:index\.php)?"
                r"\?page=post&s=view&id=(\d+)")]
    test = [("http://safebooru.org/index.php?page=post&s=view&id=1169132", {
        "url": "bcb6047665729c7c9db243a27f41cbef9af1ecef",
        "content": "93b293b27dabd198afafabbaf87c49863ac82f27",
    })]
