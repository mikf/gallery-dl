# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://reader.puremashiro.moe/"""

from . import foolslide


class PuremashiroChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from reader.puremashiro.moe"""
    category = "puremashiro"
    pattern = foolslide.chapter_pattern(r"reader\.puremashiro\.moe")
    test = [(("http://reader.puremashiro.moe"
              "/read/parallel-paradise-eng/en-us/0/20/"), {
        "url": "00d5bc9cbb413ed584ddb091ae2418ca7801b136",
        "keyword": "73bba3222758927e5a7cdc9e1db9d8307fe944c0",
    })]
    scheme = "http"


class PuremashiroMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from reader.puremashiro.moe"""
    category = "puremashiro"
    pattern = foolslide.manga_pattern(r"reader\.puremashiro\.moe")
    test = [("http://reader.puremashiro.moe/series/hayate-no-gotoku/", {
        "url": "0cf77a623bff35b43323427a8fd1e40ff0e13c09",
        "keyword": "1b57d724b259a1d81b6352d889a1aa5eb86a6ef9",
    })]
    scheme = "http"
