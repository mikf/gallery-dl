# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://jaiminisbox.com/"""

from . import foolslide


class JaiminisboxChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from jaiminisbox.com"""
    category = "jaiminisbox"
    pattern = foolslide.chapter_pattern(r"(?:www\.)?jaiminisbox.com/reader")
    test = [("https://jaiminisbox.com/reader/read/uratarou/en/0/1/", {
        "url": "f021de7f31ee3a3f688fdf3e8183aef4226c2b50",
        "keyword": "d187df3e3b6dbe09ec163626f6fd7c57133ab163",
    })]
