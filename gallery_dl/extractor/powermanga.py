# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://powermanga.org/"""

from . import foolslide


class PowermangaChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from powermanga.org"""
    category = "powermanga"
    pattern = foolslide.chapter_pattern(r"read(?:er)?\.powermanga\.org")
    test = [(("https://read.powermanga.org"
              "/read/one_piece_digital_colour_comics/en/0/75/"), {
        "url": "854c5817f8f767e1bccd05fa9d58ffb5a4b09384",
        "keyword": "9985bcb78491dff9c725958b06bba606be51b6d3",
    })]


class PowermangaMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from powermanga.org"""
    category = "powermanga"
    pattern = foolslide.manga_pattern(r"read\.powermanga\.org")
    test = [(("https://read.powermanga.org"
              "/series/one_piece_digital_colour_comics/"), {
        "count": ">= 1",
        "keyword": {
            "chapter": int,
            "chapter_minor": str,
            "chapter_string": str,
            "group": "PowerManga",
            "lang": "en",
            "language": "English",
            "manga": "One Piece Digital Colour Comics",
            "title": str,
            "volume": int,
        },
    })]
