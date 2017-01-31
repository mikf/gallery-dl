# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://yomanga.co/"""

from .foolslide import FoolslideChapterExtractor


class YomangaChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from yomanga.co"""
    category = "yomanga"
    pattern = [(r"(?:https?://)?(?:www\.)?(yomanga\.co/reader/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [("https://yomanga.co/reader/read/uwakoi/en/0/2/", {
        "url": "4b5d8fc5902f03647cc876cf6643849e5bc05455",
        "keyword": "1b9ac4217146421dbcb2a1108693054c56554a9d",
    })]
    single = False

    def __init__(self, match):
        url = "https://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
