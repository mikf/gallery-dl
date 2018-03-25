# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archive.loveisover.me/"""

from . import chan


class LoveisoverThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on archive.loveisover.me"""
    category = "loveisover"
    root = "https://archive.loveisover.me"
    pattern = [r"(?:https?://)?(?:archive\.)?loveisover\.me"
               r"/([^/]+)/thread/(\d+)"]
    test = [("https://archive.loveisover.me/c/thread/2898043/", {
        "url": "f1531a84de4e25ed3ae768384f6be43a0f02db71",
    })]
