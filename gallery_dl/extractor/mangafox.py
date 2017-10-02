# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangafox.me/"""

from .common import AsynchronousExtractor, Message
from .. import text, util, exception
import re


class MangafoxChapterExtractor(AsynchronousExtractor):
    """Extractor for manga-chapters from mangafox.me"""
    category = "mangafox"
    subcategory = "chapter"
    directory_fmt = [
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    pattern = [(r"(?:https?://)?(?:www\.)?(mangafox\.me/manga/"
                r"[^/]+/(v\d+/)?c\d+[^/]*)")]
    test = [(("http://mangafox.me/manga/kidou_keisatsu_patlabor/"
              "v05/c006.2/1.html"), {
        "keyword": "36b570e9ef11b4748407324fe08bebbe4856e6fd",
        "content": "5c50c252dcf12ffecf68801f4db8a2167265f66c",
    })]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.url = "http://" + match.group(1)

    def items(self):
        page = self.request(self.url + "/1.html").text
        if "Sorry, its licensed, and not available." in page:
            raise exception.AuthorizationError()
        data = self.get_metadata(page)
        urls = zip(
            range(1, data["count"]+1),
            self.get_image_urls(page),
        )
        yield Message.Version, 1
        yield Message.Directory, data.copy()
        for data["page"], url in urls:
            text.nameext_from_url(url, data)
            yield Message.Url, url, data.copy()

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
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
            data[key] = util.safe_int(data[key])
        return data

    def get_image_urls(self, page):
        """Yield all image-urls for this chapter"""
        pnum = 1
        while True:
            url, pos = text.extract(page, '<img src="', '"')
            yield url
            _  , pos = text.extract(page, '<img src="', '"', pos)
            url, pos = text.extract(page, '<img src="', '"', pos)
            yield url
            pnum += 2
            page = self.request(self.url + "/{}.html".format(pnum)).text
