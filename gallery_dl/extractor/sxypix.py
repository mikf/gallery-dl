# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://sxypix.com/"""

from .common import GalleryExtractor
from .. import text


class SxypixGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from sxypix.com"""
    category = "sxypix"
    root = "https://sxypix.com"
    pattern = r"(?:https?://)?(?:www\.)?sxypix\.com(/w/(\w+))"
    example = "https://sxypix.com/w/2bbaf1b24a5863d0e73436619bbaa7ee"

    def metadata(self, page):
        return {
            "gallery_id": self.groups[1],
            "title": text.unescape(text.extr(
                page, '<meta name="keywords" content="', '"')),
        }

    def images(self, page):
        data = {
            "aid"  : text.extr(page, "data-aid='", "'"),
            "ghash": text.extr(page, "data-ghash='", "'"),
        }
        gallery = self.request_json(
            "https://sxypix.com/php/gall.php", method="POST", data=data)

        base = "https://x."
        return [
            (base + text.extr(entry, "data-src='//.", "'"), None)
            for entry in gallery["r"]
        ]
