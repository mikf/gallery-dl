# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pornstars.tube/"""

from .common import GalleryExtractor
from .. import text


class PornstarstubeGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from pornstars.tube"""
    category = "pornstarstube"
    root = "https://pornstars.tube"
    pattern = (r"(?:https?://)?(?:www\.)?pornstars\.tube"
               r"/albums/(\d+)(?:/([\w-]+))?")
    example = "https://pornstars.tube/albums/12345/SLUG/"

    def __init__(self, match):
        url = f"{self.root}/albums/{match[1]}/{match[2] or 'a'}/"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        gid, slug = self.groups
        return {
            "gallery_id": text.parse_int(gid),
            "slug"      : slug or "",
            "title"     : text.unescape(text.extr(
                page, "<title>", " - PORNSTARS.TUBE</title>")),
            "description": text.unescape(text.extr(
                page, 'name="description" content="', '"')),
            "tags": text.extr(
                page, 'name="keywords" content="', '"').split(", "),
        }

    def images(self, page):
        album = text.extr(page, 'class="block-album"', "\n</div>")
        return [
            (url, None)
            for url in text.extract_iter(album, ' href="', '"')
        ]
