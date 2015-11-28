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
    pattern = [r"(?:https?://)?(?:www\.)?mangapanda\.com(/[^/]+)$"]


class MangaPandaChapterExtractor(MangaPandaBase, MangaReaderChapterExtractor):
    """Extract a single manga-chapter from mangapanda"""
    pattern = [
        r"(?:https?://)?(?:www\.)?mangapanda\.com((/[^/]+)/(\d+))",
        r"(?:https?://)?(?:www\.)?mangapanda\.com(/\d+-\d+-\d+(/[^/]+)/chapter-(\d+).html)",
    ]
