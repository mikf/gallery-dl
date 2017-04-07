# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://reader.seaotterscans.com/"""

from . import foolslide


class SeaotterscansChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from reader.seaotterscans.com"""
    category = "seaotterscans"
    pattern = foolslide.chapter_pattern("reader\.seaotterscans\.com")
    test = [("https://reader.seaotterscans.com/read/100_days/en/0/5/", {
        "url": "63d46b8883cc652dfe8bd5be4492160dd31f06a8",
        "keyword": "4d92576e23ee2a5058fd150690230091ee091868",
    })]
