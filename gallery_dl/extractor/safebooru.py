# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from http://safebooru.org/"""

from . import booru

class SafebooruExtractor(booru.XMLBooruExtractor):
    """Base class for safebooru extractors"""

    category = "safebooru"
    api_url = "http://safebooru.org/index.php"

    def setup(self):
        self.params.update({"page":"dapi", "s":"post", "q":"index"})

    def update_page(self, reset=False):
        if reset is False:
            self.params["pid"] += 1
        else:
            self.params["pid"] = 0

class SafebooruTagExtractor(SafebooruExtractor, booru.BooruTagExtractor):
    """Extract images from safebooru based on search-tags"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?(?:www\.)?safebooru\.org/(?:index\.php)?\?page=post&s=list&tags=([^&]+)"]
    test = [("http://safebooru.org/index.php?page=post&s=list&tags=heath_ledger", {
        "url": "72f17ad6f8254595b56f7e5dd1947d8b51b1ba9b",
        "keyword": "79670e1de47e39352fe71f482ece003cdf8e4512",
    })]

class SafebooruPostExtractor(SafebooruExtractor, booru.BooruPostExtractor):
    """Extract single images from safebooru"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?safebooru\.org/(?:index\.php)?\?page=post&s=view&id=(\d+)"]
    test = [("http://safebooru.org/index.php?page=post&s=view&id=1169132", {
        "url": "bcb6047665729c7c9db243a27f41cbef9af1ecef",
        "keyword": "e2d9a87a66d89eb68d3e3420075c3be3c7ca530a",
    })]
