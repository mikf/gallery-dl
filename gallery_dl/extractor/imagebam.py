# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imagebam.com/"""

from .common import Extractor, Message
from .. import text
import re


class ImagebamExtractor(Extractor):
    """Base class for imagebam extractors"""
    category = "imagebam"
    root = "https://www.imagebam.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)

    def _init(self):
        self.cookies.set("nsfw_inter", "1", domain="www.imagebam.com")

    def _parse_image_page(self, path):
        page = self.request(self.root + path).text
        url, pos = text.extract(page, '<img src="https://images', '"')
        filename = text.unescape(text.extract(page, 'alt="', '"', pos)[0])

        data = {
            "url"      : "https://images" + url,
            "image_key": path.rpartition("/")[2],
        }
        data["filename"], _, data["extension"] = filename.rpartition(".")
        return data


class ImagebamGalleryExtractor(ImagebamExtractor):
    """Extractor for imagebam galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{title} {gallery_key}")
    filename_fmt = "{num:>03} {filename}.{extension}"
    archive_fmt = "{gallery_key}_{image_key}"
    pattern = (r"(?:https?://)?(?:www\.)?imagebam\.com"
               r"(/(?:gallery/|view/G)[a-zA-Z0-9]+)")
    example = "https://www.imagebam.com/view/GID"

    def items(self):
        page = self.request(self.root + self.path).text

        images = self.images(page)
        images.reverse()

        data = self.metadata(page)
        data["count"] = len(images)
        data["gallery_key"] = self.path.rpartition("/")[2]

        yield Message.Directory, data
        for data["num"], path in enumerate(images, 1):
            image = self._parse_image_page(path)
            image.update(data)
            yield Message.Url, image["url"], image

    @staticmethod
    def metadata(page):
        return {"title": text.unescape(text.extr(
            page, 'id="gallery-name">', '<').strip())}

    def images(self, page):
        findall = re.compile(r'<a href="https://www\.imagebam\.com'
                             r'(/(?:image/|view/M)[a-zA-Z0-9]+)').findall

        paths = []
        while True:
            paths += findall(page)
            pos = page.find('rel="next" aria-label="Next')
            if pos > 0:
                url = text.rextract(page, 'href="', '"', pos)[0]
                if url:
                    page = self.request(url).text
                    continue
            return paths


class ImagebamImageExtractor(ImagebamExtractor):
    """Extractor for single imagebam images"""
    subcategory = "image"
    archive_fmt = "{image_key}"
    pattern = (r"(?:https?://)?(?:\w+\.)?imagebam\.com"
               r"(/(?:image/|view/M|(?:[0-9a-f]{2}/){3})[a-zA-Z0-9]+)")
    example = "https://www.imagebam.com/view/MID"

    def items(self):
        path = self.path
        if path[3] == "/":
            path = ("/view/" if path[10] == "M" else "/image/") + path[10:]

        image = self._parse_image_page(path)
        yield Message.Directory, image
        yield Message.Url, image["url"], image
