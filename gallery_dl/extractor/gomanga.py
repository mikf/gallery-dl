# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://gomanga.co/"""

from . import foolslide


class GomangaChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from gomanga.co"""
    category = "gomanga"
    pattern = foolslide.chapter_pattern(r"(?:www\.)?gomanga\.co/reader")
    test = [
        ("https://gomanga.co/reader/read/mata-kata-omou/en/0/1/page/11", {
            "url": "5088d75bb44327fc503c85b52b1d6a371b8057f2",
            "keyword": "f534cfc4c3aef87cb0439e2a37e2ebee98077e92",
        }),
        ("https://gomanga.co/reader/read/pastel/en/31/144/", {
            "url": "9cc2052fbf36344c573c754c5abe533a14b3e280",
            "keyword": "a2ef55d26984c64baf026382f889bb013d01dc4f",
        }),
    ]
    single = False


class GomangaMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from gomanga.co"""
    category = "gomanga"
    pattern = foolslide.manga_pattern(r"(?:www\.)?gomanga\.co/reader")
    test = [("https://gomanga.co/reader/series/pastel/", {
        "url": "bd1c82d70838d54140a8209296e789f27ceab7cd",
    })]
    single = False
