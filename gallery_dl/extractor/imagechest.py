# -*- coding: utf-8 -*-

# Copyright 2020 Leonid "Bepis" Pavel
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at https://imgchest.com/"""

from .common import GalleryExtractor
from .. import text, exception


class ImagechestGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from imgchest.com"""
    category = "imagechest"
    root = "https://imgchest.com"
    pattern = r"(?:https?://)?(?:www\.)?imgchest\.com/p/([A-Za-z0-9]{11})"
    test = (
        ("https://imgchest.com/p/3na7kr3by8d", {
            "url": "f095b4f78c051e5a94e7c663814d1e8d4c93c1f7",
            "content": "076959e65be30249a2c651fbe6090dc30ba85193",
            "count": 3
        }),
    )

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = self.root + "/p/" + self.gallery_id
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        if "Sorry, but the page you requested could not be found." in page:
            raise exception.NotFoundError("gallery")

        return {
            "gallery_id": self.gallery_id,
            "title": text.unescape(text.extract(
                page, 'property="og:title" content="', '"')[0].strip())
        }

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(
                page, 'property="og:image" content="', '"')
        ]
