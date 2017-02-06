# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://famatg.com/"""

from .foolslide import FoolslideChapterExtractor


class FallenangelsChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from famatg.com"""
    category = "fallenangels"
    pattern = [(r"(?:https?://)?((?:manga|truyen)\.famatg\.com/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+(?:/\d+)?)")]
    test = [
        ("http://manga.famatg.com/read/chronos_ruler/en/0/20/", {
            "url": "a777f93533674744b74c9b57c7dfa7254f5ddbed",
            "keyword": "47ac083cac8a3c0aaf0f6b571a9bfb535217fd31",
        }),
        ("https://truyen.famatg.com/read/madan_no_ou_to_vanadis/vi/0/33/", {
            "url": "b46bf1ef0537c3ce42bf2b9e4b62ace41c2299cd",
            "keyword": "9eb750934f4f712211f5a7063c2206693b7cedf9",
        }),
    ]

    def __init__(self, match):
        url = "https://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
