# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://reader.kireicake.com/"""

from . import foolslide


class KireicakeChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from reader.kireicake.com"""
    category = "kireicake"
    pattern = foolslide.chapter_pattern(r"reader\.kireicake\.com")
    test = [("https://reader.kireicake.com/read/wonderland/en/1/1/", {
        "url": "b2d36bc0bc67e4c461c3a4d6444a2fd339f5d07e",
        "keyword": "47e0cf69f95ab3b820bda05014aec38d3b824018",
    })]


class KireicakeMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from reader.kireicake.com"""
    category = "kireicake"
    pattern = foolslide.manga_pattern(r"reader\.kireicake\.com")
    test = [("https://reader.kireicake.com/series/wonderland/", {
        "url": "d067b649af1cc88fa8c8b698fde04a10909fd169",
        "keyword": "99caa336a9d48e27e3b8e56a0a1e6faf9fc13a51",
    })]
