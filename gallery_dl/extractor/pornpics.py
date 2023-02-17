# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pornpics.com/"""

from .common import GalleryExtractor, Extractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?pornpics\.com"


class PornpicsExtractor(Extractor):
    """Base class for pornpics extractors"""
    category = "pornpics"
    root = "https://www.pornpics.com/"

    def __init__(self, match):
        super().__init__(match)
        self.session.headers["Referer"] = self.root


class PornpicsGalleryExtractor(PornpicsExtractor, GalleryExtractor):
    """Extractor for pornpics galleries"""
    pattern = BASE_PATTERN + r"(?:/\w\w)?(/galleries/(?:[^/?#]+-)?(\d+))"
    test = (
        (("https://www.pornpics.com/galleries/british-beauty-danielle-flashes-"
          "hot-breasts-ass-and-snatch-in-the-forest-62610699/"), {
            "pattern": r"https://cdni\.pornpics\.com/1280/7/160/62610699"
                       r"/62610699_\d+_[0-9a-f]{4}\.jpg",
            "keyword": {
                "categories": ["MILF", "Amateur", "Sexy", "Outdoor"],
                "channel": "FTV MILFs",
                "count": 17,
                "gallery_id": 62610699,
                "models": ["Danielle"],
                "num": int,
                "slug": "british-beauty-danielle-flashes-"
                        "hot-breasts-ass-and-snatch-in-the-forest",
                "tags": ["Amateur MILF", "Sexy MILF"],
                "title": "British beauty Danielle flashes "
                         "hot breasts, ass and snatch in the forest",
                "views": int,
            },
        }),
        ("https://pornpics.com/es/galleries/62610699", {
            "keyword": {
                "slug": "british-beauty-danielle-flashes-"
                        "hot-breasts-ass-and-snatch-in-the-forest",
            },
        }),
    )

    def __init__(self, match):
        self.gallery_id = match.group(2)
        PornpicsExtractor.__init__(self, match)

    def metadata(self, page):
        extr = text.extract_from(page)

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "slug"      : extr("/galleries/", "/").rpartition("-")[0],
            "title"     : text.unescape(extr("<h1>", "<")),
            "channel"   : extr('>Channel:', '</a>').rpartition(">")[2],
            "models"    : text.split_html(extr(
                ">Models:", '<span class="suggest')),
            "categories": text.split_html(extr(
                ">Categories:", '<span class="suggest')),
            "tags"      : text.split_html(extr(
                ">Tags List:", ' </div>')),
            "views"    : text.parse_int(extr(">Views:", "<").replace(",", "")),
        }

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(page, "class='rel-link' href='", "'")
        ]
