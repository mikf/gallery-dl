# -*- coding: utf-8 -*-

# Copyright 2017-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://fanfox.net/"""

from .common import ChapterExtractor
from .. import text, exception
import re


class MangafoxChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from fanfox.net"""
    category = "mangafox"
    pattern = [(r"(?:https?://)?(?:www\.)?(?:mangafox\.me|fanfox\.net)"
                r"(/manga/[^/]+/(?:v\d+/)?c\d+[^/?&#]*)")]
    test = [
        ("http://fanfox.net/manga/kidou_keisatsu_patlabor/v05/c006.2/1.html", {
            "keyword": "36b570e9ef11b4748407324fe08bebbe4856e6fd",
            "content": "5c50c252dcf12ffecf68801f4db8a2167265f66c",
        }),
        ("http://mangafox.me/manga/kidou_keisatsu_patlabor/v05/c006.2/", None),
    ]
    root = "http://fanfox.net"

    def __init__(self, match):
        self.urlbase = self.root + match.group(1)
        ChapterExtractor.__init__(self, self.urlbase + "/1.html")

    def get_metadata(self, page):
        if "Sorry, its licensed, and not available." in page:
            raise exception.AuthorizationError()
        data = text.extract_all(page, (
            ("manga"         , " - Read ", " Manga Scans "),
            ("sid"           , "var sid=", ";"),
            ("cid"           , "var cid=", ";"),
            ("count"         , "var total_pages=", ";"),
            ("chapter_string", 'var current_chapter="', '"'),
        ))[0]
        match = re.match(r"(v0*(\d+)/)?c0*(\d+)(.*)", data["chapter_string"])
        data["volume"] = match.group(2)
        data["chapter"] = match.group(3)
        data["chapter_minor"] = match.group(4) or ""
        data["manga"] = data["manga"].rpartition(" ")[0]
        for key in ("sid", "cid", "count", "volume", "chapter"):
            data[key] = text.parse_int(data[key])
        return data

    def get_images(self, page):
        pnum = 1
        while True:
            url, pos = text.extract(page, '<img src="', '"')
            yield url, None
            url, pos = text.extract(page, '<img src="', '"', pos)
            yield url, None

            pnum += 2
            page = self.request("{}/{}.html".format(self.urlbase, pnum)).text
