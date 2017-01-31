# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://www.slide.world-three.org/"""

from .foolslide import FoolslideChapterExtractor


class WorldthreeChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from slide.world-three.org"""
    category = "worldthree"
    pattern = [(r"(?:https?://)?(?:www\.)?(slide\.world-three\.org/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [(("http://www.slide.world-three.org/"
              "read/black_bullet/en/2/7/page/1"), {
        "url": "be2f04f6e2d311b35188094cfd3e768583271584",
        "keyword": "6d77d9fc806d76d881491a52ccd8dfd875c47d05",
    })]

    def __init__(self, match):
        url = "http://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
