# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangapanda.com/"""

from .mangareader import MangareaderMangaExtractor, MangareaderChapterExtractor


class MangapandaBase():
    """Base class for mangapanda extractors"""
    category = "mangapanda"
    root = "http://www.mangapanda.com"


class MangapandaMangaExtractor(MangapandaBase, MangareaderMangaExtractor):
    """Extractor for manga from mangapanda.com"""
    pattern = [r"(?:https?://)?((?:www\.)?mangapanda\.com/[^/?&#]+)/?$"]
    test = [("http://www.mangapanda.com/mushishi", {
        "url": "50a1ba730b85426b904da256c80f68ba6a8a2566",
        "keyword": "031b3ea085921c552de017ecbb9b906e462229c9",
    })]


class MangapandaChapterExtractor(MangapandaBase, MangareaderChapterExtractor):
    """Extractor for manga-chapters from mangapanda.com"""
    pattern = [
        (r"(?:https?://)?(?:www\.)?mangapanda\.com((/[^/?&#]+)/(\d+))"),
        (r"(?:https?://)?(?:www\.)?mangapanda\.com"
         r"(/\d+-\d+-\d+(/[^/]+)/chapter-(\d+)\.html)"),
    ]
    test = [("http://www.mangapanda.com/red-storm/2", {
        "url": "4bf4ddf6c50105ec8a37675495ab80c46608275d",
        "keyword": "367d2694b49cc7cac82d68530d7d467a62453502",
    })]
