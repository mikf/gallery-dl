# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://sensescans.com/"""

from . import foolslide


class SensescansChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from sensescans.com"""
    category = "sensescans"
    pattern = [(r"(?:https?://)?(?:www\.|reader\.)?sensescans\.com"
                r"(?:/reader)?(" + foolslide.CHAPTER_RE)]
    test = [
        (("http://reader.sensescans.com/read/"
          "magi__labyrinth_of_magic/en/33/319/page/1"), {
              "url": "cc192cbeed36127d374926c50c3a4bd06092b760",
              "keyword": "f80104d205e3f537ca11fef9e761393c956768f0",
        }),
        (("http://sensescans.com/reader/read/"
          "magi__labyrinth_of_magic/en/33/319/page/1"), {
              "url": "cc192cbeed36127d374926c50c3a4bd06092b760",
              "keyword": "f80104d205e3f537ca11fef9e761393c956768f0",
        }),
    ]

    def __init__(self, match):
        url = "http://sensescans.com/reader" + match.group(1)
        super().__init__(match, url)
