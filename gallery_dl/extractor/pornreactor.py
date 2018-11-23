# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://pornreactor.cc/"""

from .joyreactor import (
    JoyreactorTagExtractor,
    JoyreactorUserExtractor,
    JoyreactorPostExtractor,
)


BASE_PATTERN = r"(?:https?://)?(?:www\.)?(pornreactor\.cc|fapreactor.com)"


class PornreactorTagExtractor(JoyreactorTagExtractor):
    """Extractor for tag searches on pornreactor.cc"""
    category = "pornreactor"
    pattern = [BASE_PATTERN + r"/tag/([^/?&#]+)"]
    test = [
        ("http://pornreactor.cc/tag/RiceGnat", {
            "count": ">= 120",
        }),
        ("http://fapreactor.com/tag/RiceGnat", None),
    ]


class PornreactorUserExtractor(JoyreactorUserExtractor):
    """Extractor for all posts of a user on pornreactor.cc"""
    category = "pornreactor"
    pattern = [BASE_PATTERN + r"/user/([^/?&#]+)"]
    test = [
        ("http://pornreactor.cc/user/Disillusion", {
            "url": "7e06f87f8dcce3fc7851b6d13aa55712ab45fb04",
            "keyword": "edfefb54ea4863e3731c508ae6caeb4140be0d31",
        }),
        ("http://fapreactor.com/user/Disillusion", None),
    ]


class PornreactorPostExtractor(JoyreactorPostExtractor):
    """Extractor for single posts on pornreactor.cc"""
    category = "pornreactor"
    subcategory = "post"
    pattern = [BASE_PATTERN + r"/post/(\d+)"]
    test = [
        ("http://pornreactor.cc/post/863166", {
            "url": "9e5f7b374605cbbd413f4f4babb9d1af6f95b843",
            "keyword": "6e9e4bd4e2d4f3f2c7936340ec71f8693129f809",
            "content": "3e2a09f8b5e5ed7722f51c5f423ff4c9260fb23e",
        }),
        ("http://fapreactor.com/post/863166", {
            "url": "83ff7c87741c05bcf1de6825e2b4739afeb87ed5",
            "keyword": "cf8159224fde59c1dab86677514b4aedeb533d66",
        }),
    ]
