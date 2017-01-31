# -*- coding: utf-8 -*-

# Copyright 2016, 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://yonkouprod.com/"""

from .foolslide import FoolslideChapterExtractor


class YonkouprodChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from yonkouprod.com"""
    category = "yonkouprod"
    pattern = [(r"(?:https?://)?(?:www\.)?(yonkouprod\.com/reader/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [("http://yonkouprod.com/reader/read/fairy-tail/en/0/512/", {
        "url": "7647850e2b1ad11c2baa9628755bf7f186350a0b",
        "keyword": "d079c718d6620478fa72a700fdd027f9a0f0760b",
    })]

    def __init__(self, match):
        url = "https://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
