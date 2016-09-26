# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://kobato.hologfx.com/"""

from .powermanga import PowermangaChapterExtractor

class DokireaderChapterExtractor(PowermangaChapterExtractor):
    """Extractor for manga-chapters from kobato.hologfx.com"""
    category = "dokireader"
    subcategory = "chapter"
    pattern = [(r"(?:https?://)?kobato\.hologfx\.com/reader/read/"
                r"(.+/([a-z]{2})/\d+/\d+)")]
    test = [("https://kobato.hologfx.com/reader/read/hitoribocchi_no_oo_seikatsu/en/3/34", {
        "keyword": "04b817c1d1da7d834283a7075c0f2a972dcb0d30",
    })]

    def __init__(self, match):
        PowermangaChapterExtractor.__init__(self, match)
        self.url_base = "https://kobato.hologfx.com/reader/read/"
