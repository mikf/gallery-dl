# -*- coding: utf-8 -*-

# Copyright 2021 David Hoppenbrouwers
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://wallpapercave.com/"""

import re
from .common import Extractor, Message
from .. import text


class WallpapercaveImageExtractor(Extractor):
    """Extractor for images on wallpapercave.com"""
    category = "wallpapercave"
    subcategory = "image"
    root = "https://wallpapercave.com"
    pattern = r"(?:https?://)?(?:www\.)?wallpapercave\.com"

    def __init__(self, match):
        super().__init__(match)
        self.url = match.string

    def items(self):
        page = self.request(self.url).text
        paths = re.compile(r'<a class="download" href="(.+?)">').findall(page)
        for path in paths:
            url = self.root + path
            image = {}
            yield Message.Directory, image
            yield Message.Url, url, text.nameext_from_url(url, image)
