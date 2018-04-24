# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://www.slide.world-three.org/"""

from . import foolslide


class WorldthreeChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from slide.world-three.org"""
    category = "worldthree"
    pattern = foolslide.chapter_pattern(r"(?:www\.)?slide\.world-three\.org")
    test = [
        (("http://www.slide.world-three.org"
          "/read/black_bullet/en/2/7/page/1"), {
            "url": "be2f04f6e2d311b35188094cfd3e768583271584",
            "keyword": "28edfeccc92f7ea29546d5616e689dcfcbac59d9",
        }),
        (("http://www.slide.world-three.org"
          "/read/idolmster_cg_shuffle/en/0/4/2/"), {
            "url": "6028ea5ca282744f925dfad92eeb98509f9cc78c",
            "keyword": "d478e9f20847deb1844dba318acaa8b91c19468a",
        }),
    ]
    scheme = "http"


class WorldthreeMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from slide.world-three.org"""
    category = "worldthree"
    pattern = foolslide.manga_pattern(r"(?:www\.)?slide\.world-three\.org")
    test = [("http://www.slide.world-three.org/series/black_bullet/", {
        "url": "5743b93512d26e6b540d90a7a5d69208b6d4a738",
        "keyword": "3a24f1088b4d7f3b798a96163f21ca251293a120",
    })]
    scheme = "http"
