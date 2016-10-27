# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://reader.sensescans.com/"""

from .foolslide import FoolslideChapterExtractor

class SensescansChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from reader.sensescans.com"""
    category = "sensescans"
    pattern = [(r"(?:https?://)?(reader\.sensescans\.com/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [("http://reader.sensescans.com/read/magi__labyrinth_of_magic/en/33/319/page/1", {
        "url": "fff6186aca61017aeb5c743cdfccac4b9b1f2557",
        "keyword": "77f906f04bf49d3bd636e8c92d85dc25aa361754",
    })]

    def __init__(self, match):
        url = "http://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
