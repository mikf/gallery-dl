# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://yomanga.co/"""

from . import foolslide


class YomangaChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from yomanga.co"""
    category = "yomanga"
    pattern = foolslide.chapter_pattern(r"(?:www\.)?yomanga\.co/reader")
    test = [("https://yomanga.co/reader/read/uwakoi/en/0/2/", {
        "url": "4b5d8fc5902f03647cc876cf6643849e5bc05455",
    })]
    single = False


class YomangaMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from yomanga.co"""
    category = "yomanga"
    pattern = foolslide.manga_pattern(r"(?:www\.)?yomanga\.co/reader")
    test = [("https://yomanga.co/reader/series/6_weapons/", {
        "url": "19a4828d3a06a4c89c885847c83af54ec1add0f7",
    })]
