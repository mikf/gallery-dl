# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://erooups.com/"""

from .common import GalleryExtractor
from .. import text


class ErooupsGalleryExtractor(GalleryExtractor):
    category = "erooups"
    directory_fmt = ("{category}", "{title}")
    archive_fmt = "{date}_{filename}"
    pattern = (r"(?:http?://)?(?:www\.)?erooups\.com"
               r"/(\d+)/(\d+)/(\d+)/([^/?#]+)")
    root = "http://erooups.com"
    example = "http://erooups.com/2023/10/25/page-title-11-pics.html"

    def __init__(self, match):
        self.year = match.group(1)
        self.month = match.group(2)
        self.day = match.group(3)
        self.slug = match.group(4)
        url = "{}/{}/{}/{}/{}".format(
            self.root, self.year, self.month, self.day, self.slug)
        GalleryExtractor.__init__(self, match, url)

    def images(self, page):
        extr = text.extr(page, 'class="imgs">', "</section>")
        return [
            (self.root + i if "erooups" not in i else i, None) for i in
            text.extract_iter(extr, 'img src="', '"')
        ]

    def metadata(self, page):
        return {
            "pageurl": self.url,
            "date": text.parse_datetime(
                "{}-{}-{}".format(self.year, self.month, self.day)),
            "title": text.extr(
                page, '<h1 class="title">', "</h1>"),
            "tag": text.extr(
                page, '"><strong>', "</strong></a>"),
            "count": text.parse_int(text.extr(
                page, '<div class="pics">', "</div>")),
        }
