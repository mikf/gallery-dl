# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://www.mangapanda.com/"""

from .mangareader import MangareaderMangaExtractor, MangareaderChapterExtractor


class MangapandaBase():
    """Base class for mangapanda extractors"""
    category = "mangapanda"
    root = "https://www.mangapanda.com"


class MangapandaChapterExtractor(MangapandaBase, MangareaderChapterExtractor):
    """Extractor for manga-chapters from mangapanda.com"""
    pattern = r"(?:https?://)?(?:www\.)?mangapanda\.com((/[^/?&#]+)/(\d+))"
    test = ("https://www.mangapanda.com/red-storm/2", {
        "url": "1f633f776e950531ba9b1e81965316458e785261",
        "keyword": "b24df4b9cc36383fb6a44e06d32a3884a4dcb5fb",
    })


class MangapandaMangaExtractor(MangapandaBase, MangareaderMangaExtractor):
    """Extractor for manga from mangapanda.com"""
    chapterclass = MangapandaChapterExtractor
    pattern = r"(?:https?://)?(?:www\.)?mangapanda\.com(/[^/?&#]+)/?$"
    test = ("https://www.mangapanda.com/mushishi", {
        "url": "357f965732371cac1990fee8b480f62e29141a42",
        "keyword": "031b3ea085921c552de017ecbb9b906e462229c9",
    })
