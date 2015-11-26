# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://www.mangapanda.com/"""

from .mangareader import *

class MangaPandaBase():

    category = "mangapanda"
    url_base = "http://www.mangapanda.com"


class MangaPandaMangaExtractor(MangaPandaBase, MangaReaderMangaExtractor):

    pattern = [r"(?:https?://)?(?:www\.)?mangapanda\.com(/[^/]+)"]


class MangaPandaChapterExtractor(MangaPandaBase, MangaReaderChapterExtractor):

    pattern = [
        r"(?:https?://)?(?:www\.)?mangapanda\.com((/[^/]+)/(\d+))",
        r"(?:https?://)?(?:www\.)?mangapanda\.com(/\d+-\d+-\d+(/[^/]+)/chapter-(\d+).html)",
    ]
