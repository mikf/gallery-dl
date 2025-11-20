# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.eporner.com/"""

from .common import GalleryExtractor
from .. import text


class EpornerGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from eporner.com"""
    category = "eporner"
    root = "https://eporner.com"
    pattern = (r"(?:https?://)?(?:www\.)?eporner\.com"
               r"/gallery/(\w+)(?:/([\w-]+))?")
    example = "https://www.eporner.com/gallery/GID/SLUG/"

    def __init__(self, match):
        url = f"{self.root}/gallery/{match[1]}/{match[2]}/"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = text.extr(page, "<title>", " - EPORNER</title>")
        if title.endswith(" Photo Gallery"):
            title = title[:-14]

        return {
            "gallery_id": self.groups[0],
            "title"     : text.unescape(title),
            "slug"      : text.extr(
                page, "/gallery/", '/"').rpartition("/")[2],
            "description": text.unescape(text.extr(
                page, 'name="description" content="', '"')),
            "tags": text.extr(
                page, 'EP.ads.keywords = "', '"').split(","),
        }

    def images(self, page):
        album = text.extr(
            page, 'class="photosgrid gallerygrid"', "id='gallerySlideBox'")

        results = []
        for url in text.extract_iter(album, ' src="', '"'):
            url, _, ext = url.rpartition(".")
            # Preview images have a resolution suffix.
            # E.g. "11208293-image-3_296x1000.jpg".
            # The same name, but without the suffix, leads to the full image.
            url = url[:url.rfind("_")]
            name = url[url.rfind("/")+1:]
            results.append((f"{url}.{ext}", {"id": name[:name.find("-")]}))
        return results
