# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bbc.co.uk/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?bbc\.co\.uk(/programmes/"


class BbcGalleryExtractor(GalleryExtractor):
    """Extractor for a programme gallery on bbc.co.uk"""
    category = "bbc"
    root = "https://www.bbc.co.uk"
    directory_fmt = ("{category}", "{path[0]}", "{path[1]}", "{path[2]}",
                     "{path[3:]:J - /}")
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "{programme}_{num}"
    pattern = BASE_PATTERN + r"[^/?#]+(?!/galleries)(?:/[^/?#]+)?)$"
    example = "https://www.bbc.co.uk/programmes/PATH"

    def metadata(self, page):
        data = self._extract_jsonld(page)

        return {
            "title": text.unescape(text.extr(
                page, "<h1>", "</h1>").rpartition("</span>")[2]),
            "description": text.unescape(text.extr(
                page, 'property="og:description" content="', '"')),
            "programme": self.gallery_url.split("/")[4],
            "path": list(util.unique_sequence(
                element["name"]
                for element in data["itemListElement"]
            )),
        }

    def images(self, page):
        width = self.config("width")
        width = width - width % 16 if width else 1920
        dimensions = "/{}xn/".format(width)

        results = []
        for img in text.extract_iter(page, 'class="gallery__thumbnail', ">"):
            src = text.extr(img, 'data-image-src="', '"')
            results.append((
                src.replace("/320x180_b/", dimensions),
                {
                    "title_image": text.unescape(text.extr(
                        img, 'data-gallery-title="', '"')),
                    "synopsis": text.unescape(text.extr(
                        img, 'data-gallery-synopsis="', '"')),
                    "_fallback": self._fallback_urls(src, width),
                },
            ))
        return results

    @staticmethod
    def _fallback_urls(src, max_width):
        front, _, back = src.partition("/320x180_b/")
        for width in (1920, 1600, 1280, 976):
            if width < max_width:
                yield "{}/{}xn/{}".format(front, width, back)


class BbcProgrammeExtractor(Extractor):
    """Extractor for all galleries of a bbc programme"""
    category = "bbc"
    subcategory = "programme"
    root = "https://www.bbc.co.uk"
    pattern = BASE_PATTERN + r"[^/?#]+/galleries)(?:/?\?page=(\d+))?"
    example = "https://www.bbc.co.uk/programmes/ID/galleries"

    def items(self):
        path, pnum = self.groups
        data = {"_extractor": BbcGalleryExtractor}
        params = {"page": text.parse_int(pnum, 1)}
        galleries_url = self.root + path

        while True:
            page = self.request(galleries_url, params=params).text
            for programme_id in text.extract_iter(
                    page, '<a href="https://www.bbc.co.uk/programmes/', '"'):
                url = "https://www.bbc.co.uk/programmes/" + programme_id
                yield Message.Queue, url, data
            if 'rel="next"' not in page:
                return
            params["page"] += 1
