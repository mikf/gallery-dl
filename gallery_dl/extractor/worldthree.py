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
    pattern = foolslide.chapter_pattern("(?:www\.)?slide\.world-three\.org")
    test = [
        (("http://www.slide.world-three.org"
          "/read/black_bullet/en/2/7/page/1"), {
            "url": "be2f04f6e2d311b35188094cfd3e768583271584",
            "keyword": "25fd070bc93ee8ad316f5b7d1bd9011c9bcf0616",
        }),
        (("http://www.slide.world-three.org"
          "/read/idolmster_cg_shuffle/en/0/4/2/"), {
            "url": "6028ea5ca282744f925dfad92eeb98509f9cc78c",
            "keyword": "10e3dc961ac2c9395f4d1f3ad3b9ad84113e7366",
        }),
    ]
    scheme = "http"


class WorldthreeMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from slide.world-three.org"""
    category = "worldthree"
    pattern = foolslide.manga_pattern("(?:www\.)?slide\.world-three\.org")
    test = [("http://www.slide.world-three.org/series/black_bullet/", {
        "url": "5743b93512d26e6b540d90a7a5d69208b6d4a738",
    })]
    scheme = "http"
