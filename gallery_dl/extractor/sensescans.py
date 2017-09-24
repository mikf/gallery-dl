# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://sensescans.com/"""

from . import foolslide


class SensescansExtractor():
    """Base class for extractors for sensescans.com"""
    category = "sensescans"

    def __init__(self, match):
        url = "http://sensescans.com/reader" + match.group(1)
        super().__init__(match, url)


class SensescansChapterExtractor(SensescansExtractor,
                                 foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from sensescans.com"""
    pattern = [(r"(?:https?://)?(?:www\.|reader\.)?sensescans\.com"
                r"(?:/reader)?(" + foolslide.CHAPTER_RE)]
    test = [
        (("http://reader.sensescans.com/read/"
          "magi__labyrinth_of_magic/en/33/319/page/1"), {
              "url": "cc192cbeed36127d374926c50c3a4bd06092b760",
              "keyword": "fcc1ff4a902f222364df9c39db2f8e7dcbcd53da",
        }),
        (("http://sensescans.com/reader/read/"
          "magi__labyrinth_of_magic/en/33/319/page/1"), {
              "url": "cc192cbeed36127d374926c50c3a4bd06092b760",
              "keyword": "fcc1ff4a902f222364df9c39db2f8e7dcbcd53da",
        }),
    ]


class SensescansMangaExtractor(SensescansExtractor,
                               foolslide.FoolslideMangaExtractor):
    """Extractor for manga from sensescans.com"""
    pattern = [(r"(?:https?://)?(?:www\.|reader\.)?sensescans\.com"
                r"(?:/reader)?(" + foolslide.MANGA_RE)]
    test = [("http://sensescans.com/reader/series/hakkenden/", {
        "url": "2360ccb0ead0ff2f5e27b7aef7eb17b9329de2f2",
        "keyword": "122cf92c32e6428c50f56ffaf29d06b96750ed71",
    })]
