# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://gomanga.co/"""

from .foolslide import FoolslideChapterExtractor


class GomangaChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from gomanga.co"""
    category = "gomanga"
    pattern = [(r"(?:https?://)?(?:www\.)?(gomanga\.co/reader/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [("https://gomanga.co/reader/read/mata-kata-omou/en/0/1/page/11", {
        "url": "5088d75bb44327fc503c85b52b1d6a371b8057f2",
        "keyword": "63f4d2cbbcaf3e7b5c48e71c4c4d453d9a399a26",
    })]
    single = False

    def __init__(self, match):
        url = "https://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
