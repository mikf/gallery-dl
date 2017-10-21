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
            "keyword": "10624e78924c37fd39543270a6965f2082bde08f",
        }),
        ("https://gomanga.co/reader/read/pastel/en/31/144/", {
            "url": "9cc2052fbf36344c573c754c5abe533a14b3e280",
            "keyword": "a355cd3197e70c24b84d3885e8a5ff0ac22537bf",
        }),
    ]
    method = "double"


class GomangaMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from gomanga.co"""
    category = "gomanga"
    pattern = foolslide.manga_pattern(r"(?:www\.)?gomanga\.co/reader")
    test = [("https://gomanga.co/reader/series/pastel/", {
        "url": "bd1c82d70838d54140a8209296e789f27ceab7cd",
        "keyword": "fb1fd14548602dbe4f6e70a633429762972c1d5d",
    })]
