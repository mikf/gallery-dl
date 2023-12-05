# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://urlgalleries.net/"""

from .common import GalleryExtractor
from .. import text


class UrlgalleriesExtractor(GalleryExtractor):
    """Base class for Urlgalleries extractors"""
    category = "urlgalleries"
    root = "urlgalleries.net"
    directory_fmt = ("{category}", "{title}")
    pattern = r"(?:https?://)([^/?#]+)?\.urlgalleries\.net/([^/?#]+)/([^/?#]+)"
    example = "https://blog.urlgalleries.net/gallery-1234567/a-title--1234"

    def __init__(self, match):
        self.blog = match.group(1)
        self.gallery_id = match.group(2)
        self.title = match.group(3)
        url = "{}.urlgalleries.net/{}/{}&a=10000".format(
            self.blog, self.gallery_id, self.title)
        GalleryExtractor.__init__(self, match, text.ensure_http_scheme(url))

    def images(self, page):
        extr = text.extr(page, 'id="wtf"', "</div>")
        url = "{}{{}}".format(self.root).format
        return [
            (text.ensure_http_scheme(url(i)), None)
            for i in text.extract_iter(extr, "href='", "'")
        ]

    def metadata(self, page):
        date = text.extr(
            page, "float:left;'>  ", '</div>').split(" | ")[-1]
        return {
            'title': self.title,
            'date': text.parse_datetime(date, format='%B %d, %Y T%H:%M')
        }
