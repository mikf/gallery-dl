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

    def __init__(self, match):
        url = "http://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
