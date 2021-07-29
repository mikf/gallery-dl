# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bbc.co.uk/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import json

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
    test = (
        ("https://www.bbc.co.uk/programmes/p084qtzs/p085g9kg", {
            "pattern": r"https://ichef\.bbci\.co\.uk"
                       r"/images/ic/1920xn/\w+\.jpg",
            "count": 37,
            "keyword": {
                "programme": "p084qtzs",
                "path": ["BBC One", "Doctor Who", "The Timeless Children"],
            },
        }),
        ("https://www.bbc.co.uk/programmes/p084qtzs"),
    )

    def metadata(self, page):
        data = json.loads(text.extract(
            page, '<script type="application/ld+json">', '</script>')[0])
        return {
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

        return [
            (src.replace("/320x180_b/", dimensions),
             {"_fallback": self._fallback_urls(src, width)})
            for src in text.extract_iter(page, 'data-image-src="', '"')
        ]

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
    test = (
        ("https://www.bbc.co.uk/programmes/b006q2x0/galleries", {
            "pattern": BbcGalleryExtractor.pattern,
            "range": "1-50",
            "count": ">= 50",
        }),
        ("https://www.bbc.co.uk/programmes/b006q2x0/galleries?page=40", {
            "pattern": BbcGalleryExtractor.pattern,
            "count": ">= 100",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path, self.page = match.groups()

    def items(self):
        data = {"_extractor": BbcGalleryExtractor}
        params = {"page": text.parse_int(self.page, 1)}
        galleries_url = self.root + self.path

        while True:
            page = self.request(galleries_url, params=params).text
            for programme_id in text.extract_iter(
                    page, '<a href="https://www.bbc.co.uk/programmes/', '"'):
                url = "https://www.bbc.co.uk/programmes/" + programme_id
                yield Message.Queue, url, data
            if 'rel="next"' not in page:
                return
            params["page"] += 1
