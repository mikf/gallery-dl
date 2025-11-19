# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://sxypix.com/"""

from .common import GalleryExtractor
from .. import text


class SxypixGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from sxypix.com"""
    root = "https://sxypix.com"
    category = "sxypix"
    pattern = r"(?:https?://)?(?:www\.)?(sxypix\.com/w/(\w+))"
    example = "https://sxypix.com/w/2bbaf1b24a5863d0e73436619bbaa7ee"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.page_url = f"https://{match[1]}"

    def metadata(self, page):
        return {
            "gallery_id": self.match[2],
            "title": text.extract(page, '<meta name="keywords" content="', '" />')[0],
        }

    def images(self, page):
        data = {
            "aid": text.extract(page, "data-aid='", "' ")[0],
            "ghash": text.extract(page, "data-ghash='", "' ")[0],
        }
        resp = self.request("https://sxypix.com/php/gall.php", method="POST", data=data)

        for entry in resp.json()["r"]:
            url = text.extract(entry, "img data-src=\'//.", "\'")[0]
            url = f"https://x.{url}"
            yield url, None
