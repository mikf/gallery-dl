# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://kobato.hologfx.com/"""

from .foolslide import FoolslideChapterExtractor

class SensescansChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from kobato.hologfx.com"""
    category = "sensescans"
    pattern = [(r"(?:https?://)?(reader\.sensescans\.com/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]

    def __init__(self, match):
        url = "http://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
