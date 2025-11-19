# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ok.porn/"""

from .common import GalleryExtractor
from .. import text


class OkpornGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from ok.porn"""
    category = "okporn"
    root = "https://ok.porn"
    pattern = r"(?:https?://)?(?:www\.)?ok\.porn/albums/(\d+)"
    example = "https://ok.porn/albums/12345/"

    def __init__(self, match):
        url = f"{self.root}/albums/{match[1]}/"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "gallery_id" : text.parse_int(self.groups[0]),
            "title"      : text.unescape(text.extr(
                page, "h1 class=title>", "</h1>")),
            "description": text.unescape(text.extr(
                page, 'name="description" content="', '"')),
            "tags": text.extr(
                page, 'name="keywords" content="', '"').split(", "),
        }

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(page, 'data-original="', '"')
        ]
