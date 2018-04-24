# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://reader.seaotterscans.com/"""

from . import foolslide


class SeaotterscansChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from reader.seaotterscans.com"""
    category = "seaotterscans"
    pattern = foolslide.chapter_pattern(r"reader\.seaotterscans\.com")
    test = [("https://reader.seaotterscans.com/read/100_days/en/0/5/", {
        "url": "63d46b8883cc652dfe8bd5be4492160dd31f06a8",
        "keyword": "5349c2fbaa88070e6af600de17a6c4e212243e8e",
    })]


class SeaotterscansMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from reader.seaotterscans.com"""
    category = "seaotterscans"
    pattern = foolslide.manga_pattern(r"reader\.seaotterscans\.com")
    test = [("https://reader.seaotterscans.com/series/marry_me/", {
        "url": "fdbacabfa566a6baeb3f01bb46cbda0577bd4bbe",
        "keyword": "61d3388d73df12f64361892b47a9398df4a5947c",
    })]
