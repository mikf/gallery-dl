# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-gallery from https://myhentaigallery.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util, exception


class MyHentaiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from myhentaigallery.com"""
    category = "myhentaigallery"
    directory_fmt = ("{category}", "{gallery_id} [{artist}] {title}")
    pattern = (r"(?:https?://)?(myhentaigallery\.com"
               r"/gallery/thumbnails/[0-9]+)")
    test = (
        ("https://myhentaigallery.com/gallery/thumbnails/16247"),
        ("https://myhentaigallery.com/gallery/thumbnails/15224"),
    )

    def __init__(self, match):
        url = "https://" + match.group(1)
        GalleryExtractor.__init__(self, match, url)
        self.session.headers["Referer"] = url

    def metadata(self, page):
        extr = text.extract_from(page)
        split = text.split_html

        image = extr('<div class="comic-cover">\n<a href="', '"')
        title = extr('<div class="comic-description">\n<h1>', '</h1>')
        if not title:
            raise exception.NotFoundError("gallery")
        data = {
            "title"     : text.unescape(title),
            "gallery_id": text.parse_int(image.split("/")[-2]),
            "tags"      : split(extr('<div>\nCategories:', '</div>')),
        }
        artists = split(extr('<div>\nArtists:', '</div>'))
        data["artist"] = artists[0] if artists else "Unknown"
        return data

    def images(self, page):
        extr = text.extract_iter
        return [
            (text.unescape(url).replace("/thumbnail/", "/original/"), None)
            for url in extr(page, 'class="comic-thumb">\n<img src="', '"')
        ]
