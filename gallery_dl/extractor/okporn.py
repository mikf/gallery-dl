# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ok.porn/"""

from .common import GalleryExtractor, Message
from .. import text


class OkpornGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from ok.porn"""
    category = "okporn"
    root = "https://ok.porn"
    pattern = r"(?:https?://)?(?:www\.)?(ok\.porn/albums/(\d+/))"
    example = "https://ok.porn/albums/66141/"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.page_url = f"https://{match[1]}"

    def metadata(self, page):
        title = text.extract(page, "h1 class=title>", "</h1>")[0]
        description = text.extract(page, '<div class="desc"', '.</div>')[0]
        return {
            "gallery_id" : text.parse_int(self.page_url.split("/")[-2]),
            "title"      : title,
            "description": description,
        }

    def images(self, page):
        page = self.request(self.page_url).text
        for url in text.extract_iter(page, 'data-original="', '"'):
            yield url, None
