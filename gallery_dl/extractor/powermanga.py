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
    test = [("https://read.powermanga.org/read/one_piece/en/0/803/page/1", {
        "url": "e6179c1565068f99180620281f86bdd25be166b4",
        "keyword": "224cab1f946d976ddbe4ef88fa1c02303699910b",
    })]


class PowermangaMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from powermanga.org"""
    category = "powermanga"
    pattern = foolslide.manga_pattern(r"read\.powermanga\.org")
    test = [("https://read.powermanga.org/series/one_piece/", {
        "count": ">= 1",
        "keyword": {
            "chapter": int,
            "chapter_minor": str,
            "chapter_string": str,
            "group": "PowerManga",
            "lang": "en",
            "language": "English",
            "manga": "One Piece",
            "title": str,
            "volume": int,
        },
    })]
