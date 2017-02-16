# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://kobato.hologfx.com/"""

from . import foolslide


class DokireaderChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from kobato.hologfx.com"""
    category = "dokireader"
    pattern = foolslide.chapter_pattern("kobato\.hologfx\.com/reader")
    test = [(("https://kobato.hologfx.com/reader/read/"
              "hitoribocchi_no_oo_seikatsu/en/3/34"), {
        "keyword": "f28811c01b64031671108a4a3d6eea1040816b82",
    })]
