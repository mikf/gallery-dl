# -*- coding: utf-8 -*-

# Copyright 2017-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://fanfox.net/"""

from .common import ChapterExtractor
from .. import text


class MangafoxChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from fanfox.net"""
    category = "mangafox"
    pattern = (r"(?:https?://)?(?:www\.|m\.)?(?:mangafox\.me|fanfox\.net)"
               r"(/manga/[^/]+/((?:v(\d+)/)?c(\d+)([^/?#]*)))")
    test = (
        ("http://fanfox.net/manga/kidou_keisatsu_patlabor/v05/c006.2/1.html", {
            "keyword": "5661dab258d42d09d98f194f7172fb9851a49766",
            "content": "5c50c252dcf12ffecf68801f4db8a2167265f66c",
        }),
        ("http://mangafox.me/manga/kidou_keisatsu_patlabor/v05/c006.2/"),
    )
    root = "https://m.fanfox.net"

    def __init__(self, match):
        base, self.cstr, self.volume, self.chapter, self.minor = match.groups()
        self.urlbase = self.root + base
        ChapterExtractor.__init__(self, match, self.urlbase + "/1.html")

    def metadata(self, page):
        manga, pos = text.extract(page, "<title>", "</title>")
        count, pos = text.extract(
            page, ">", "<", page.find("</select>", pos) - 20)
        sid  , pos = text.extract(page, "var series_id =", ";", pos)
        cid  , pos = text.extract(page, "var chapter_id =", ";", pos)

        return {
            "manga": text.unescape(manga),
            "volume": text.parse_int(self.volume),
            "chapter": text.parse_int(self.chapter),
            "chapter_minor": self.minor or "",
            "chapter_string": self.cstr,
            "count": text.parse_int(count),
            "sid": text.parse_int(sid),
            "cid": text.parse_int(cid),
        }

    def images(self, page):
        pnum = 1
        while True:
            url, pos = text.extract(page, '<img src="', '"')
            yield text.ensure_http_scheme(url), None
            url, pos = text.extract(page, ' src="', '"', pos)
            yield text.ensure_http_scheme(url), None

            pnum += 2
            page = self.request("{}/{}.html".format(self.urlbase, pnum)).text
