# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://myhentaigallery.com/"""

from .common import Extractor, GalleryExtractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?myhentaigallery\.com"


class MyhentaigalleryBase():
    category = "myhentaigallery"
    root = "https://myhentaigallery.com"


class MyhentaigalleryGalleryExtractor(MyhentaigalleryBase, GalleryExtractor):
    """Extractor for image galleries from myhentaigallery.com"""
    directory_fmt = ("{category}", "{gallery_id} {artist:?[/] /J, }{title}")
    pattern = rf"{BASE_PATTERN}/g(?:allery/(?:thumbnails|show))?/(\d+)"
    example = "https://myhentaigallery.com/g/12345"

    def __init__(self, match):
        self.gallery_id = match[1]
        url = f"{self.root}/g/{self.gallery_id}"
        GalleryExtractor.__init__(self, match, url)

    def _init(self):
        self.session.headers["Referer"] = self.page_url

    def metadata(self, page):
        extr = text.extract_from(page)
        split = text.split_html

        title = extr('<div class="comic-description">\n', '</h1>').lstrip()
        if title.startswith("<h1>"):
            title = title[4:]

        if not title:
            raise exception.NotFoundError("gallery")

        return {
            "title"     : text.unescape(title),
            "gallery_id": text.parse_int(self.gallery_id),
            "tags"      : split(extr("        Categories:", "</div>")),
            "artist"    : split(extr("        Artists:"   , "</div>")),
            "group"     : split(extr("        Groups:"    , "</div>")),
            "parodies"  : split(extr("        Parodies:"  , "</div>")),
        }

    def images(self, page):
        return [
            (text.unescape(text.extr(url, 'src="', '"')).replace(
                "/thumbnail/", "/original/"), None)
            for url in text.extract_iter(page, 'class="comic-thumb"', '</div>')
        ]


class MyhentaigalleryTagExtractor(MyhentaigalleryBase, Extractor):
    """Extractor for myhentaigallery tag searches"""
    subcategory = "tag"
    pattern = rf"{BASE_PATTERN}(/g/(artist|category|group|parody)/(\d+).*)"
    example = "https://myhentaigallery.com/g/category/123"

    def items(self):
        data = {"_extractor": MyhentaigalleryGalleryExtractor}
        for url in self.galleries():
            yield Message.Queue, url, data

    def galleries(self):
        root = self.root
        url = root + self.groups[0]

        while True:
            page = self.request(url).text

            for inner in text.extract_iter(
                    page, '<div class="comic-inner">', "<div"):
                yield root + text.extr(inner, 'href="', '"')

            try:
                pos = page.index(">Next<")
            except ValueError:
                return
            url = root + text.rextr(page, 'href="', '"', pos)
