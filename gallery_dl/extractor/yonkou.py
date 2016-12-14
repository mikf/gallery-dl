# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://yonkouprod.com/"""

from .foolslide import FoolslideChapterExtractor

class YonkouChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from yonkouprod.com"""
    category = "yonkou"
    pattern = [(r"(?:https?://)?(?:www\.)?(yonkouprod\.com/reader/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [("http://yonkouprod.com/reader/read/fairy-tail/en/0/512/", {
        "url": "7647850e2b1ad11c2baa9628755bf7f186350a0b",
        "keyword": "2e3519670694bd851149f8004a00320b9e962044",
    })]

    def __init__(self, match):
        url = "https://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
