# -*- coding: utf-8 -*-

# Copyright 2021 David Hoppenbrouwers
# Copyright 2023 Mike Fährmann
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
    pattern = r"(?:https?://)?(?:www\.)?wallpapercave\.com/"
    example = "https://wallpapercave.com/w/wp12345"

    def items(self):
        page = self.request(text.ensure_http_scheme(self.url)).text

        path = None
        for path in text.extract_iter(page, 'class="download" href="', '"'):
            image = text.nameext_from_url(path)
            yield Message.Directory, image
            yield Message.Url, self.root + path, image

        if path is None:
            try:
                path = text.rextract(
                    page, 'href="', '"', page.index('id="tdownload"'))[0]
            except Exception:
                pass
            else:
                image = text.nameext_from_url(path)
                yield Message.Directory, image
                yield Message.Url, self.root + path, image

        if path is None:
            for wp in text.extract_iter(
                    page, 'class="wallpaper" id="wp', '</picture>'):
                path = text.rextract(wp, ' src="', '"')[0]
                if path:
                    image = text.nameext_from_url(path)
                    yield Message.Directory, image
                    yield Message.Url, self.root + path, image
