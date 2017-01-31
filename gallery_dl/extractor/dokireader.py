# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://kobato.hologfx.com/"""

from .foolslide import FoolslideChapterExtractor


class DokireaderChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from kobato.hologfx.com"""
    category = "dokireader"
    pattern = [(r"(?:https?://)?(kobato\.hologfx\.com/reader/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [(("https://kobato.hologfx.com/reader/read/"
              "hitoribocchi_no_oo_seikatsu/en/3/34"), {
        "keyword": "4ee981ae14c6643f6a03a14c9f2c0d4898202671",
    })]

    def __init__(self, match):
        url = "https://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
