# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archive.4plebs.org/"""

from . import chan


class FourplebsThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on 4plebs.org"""
    category = "4plebs"
    root = "https://archive.4plebs.org"
    pattern = [r"(?:https?://)?(?:archive\.)?4plebs\.org/([^/]+)/thread/(\d+)"]
    test = [("https://archive.4plebs.org/tg/thread/54059290", {
        "url": "fd823f17b5001442b941fddcd9ec91bafedfbc79",
    })]
