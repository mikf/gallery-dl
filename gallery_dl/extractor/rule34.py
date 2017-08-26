# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://rule34.xxx/"""

from . import booru


class Rule34Extractor(booru.XMLBooruExtractor):
    """Base class for rule34 extractors"""
    category = "rule34"
    api_url = "https://rule34.xxx/index.php"
    pagestart = 0
    pagekey = "pid"

    def setup(self):
        self.params.update({"page": "dapi", "s": "post", "q": "index"})


class Rule34TagExtractor(Rule34Extractor, booru.BooruTagExtractor):
    """Extractor for images from rule34.xxx based on search-tags"""
    pattern = [(r"(?:https?://)?(?:www\.)?rule34\.xxx/(?:index\.php)?"
                r"\?page=post&s=list&tags=([^&]+)")]
    test = [("http://rule34.xxx/index.php?page=post&s=list&tags=danraku", {
        "url": "104094495973edfe7e764c8f2dd42017163322aa",
        "content": "a01768c6f86f32eb7ebbdeb87c30b0d9968d7f97",
    })]


class Rule34PostExtractor(Rule34Extractor, booru.BooruPostExtractor):
    """Extractor for single images from rule34.xxx"""
    pattern = [(r"(?:https?://)?(?:www\.)?rule34\.xxx/(?:index\.php)?"
                r"\?page=post&s=view&id=(\d+)")]
    test = [("http://rule34.xxx/index.php?page=post&s=view&id=1974854", {
        "url": "3b1f9817785868d1cd94d5376d20478eed591965",
        "content": "fd2820df78fb937532da0a46f7af6cefc4dc94be",
    })]
