# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangapanda.com/"""

from .mangareader import MangaReaderMangaExtractor, MangaReaderChapterExtractor

class MangaPandaBase():
    """Base class for mangapanda extractors"""
    category = "mangapanda"
    url_base = "http://www.mangapanda.com"


class MangaPandaMangaExtractor(MangaPandaBase, MangaReaderMangaExtractor):
    """Extract all manga-chapters from mangapanda"""
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?mangapanda\.com(/[^/]+)$"]
    test = [("http://www.mangapanda.com/mushishi", {
        "url": "50a1ba730b85426b904da256c80f68ba6a8a2566",
    })]

class MangaPandaChapterExtractor(MangaPandaBase, MangaReaderChapterExtractor):
    """Extract a single manga-chapter from mangapanda"""
    subcategory = "chapter"
    pattern = [
        r"(?:https?://)?(?:www\.)?mangapanda\.com((/[^/]+)/(\d+))",
        r"(?:https?://)?(?:www\.)?mangapanda\.com(/\d+-\d+-\d+(/[^/]+)/chapter-(\d+).html)",
    ]
    test = [("http://www.mangapanda.com/red-storm/2", {
        "url": "4bf4ddf6c50105ec8a37675495ab80c46608275d",
        "keyword": "dcb8d655e3f461738c821819bbb8d017bd916713",
    })]
