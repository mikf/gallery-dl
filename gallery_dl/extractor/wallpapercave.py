# -*- coding: utf-8 -*-

# Copyright 2021 David Hoppenbrouwers
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://wallpapercave.com/"""

from .common import Extractor, Message
from .. import text


class WallpapercaveImageExtractor(Extractor):
    """Extractor for images on wallpapercave.com"""
    category = "wallpapercave"
    subcategory = "image"
    root = "https://wallpapercave.com"
    pattern = r"(?:https?://)?(?:www\.)?wallpapercave\.com"
    test = ("https://wallpapercave.com/w/wp10270355", {
        "content": "58b088aaa1cf1a60e347015019eb0c5a22b263a6",
    })

    def items(self):
        page = self.request(text.ensure_http_scheme(self.url)).text
        for path in text.extract_iter(page, 'class="download" href="', '"'):
            image = text.nameext_from_url(path)
            yield Message.Directory, image
            yield Message.Url, self.root + path, image
