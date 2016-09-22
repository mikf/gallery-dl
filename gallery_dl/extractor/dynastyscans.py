# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://dynasty-scans.com/"""

from .common import Extractor, Message
from .. import text
import re
import json

class DynastyscansChapterExtractor(Extractor):
    """Extractor for manga-chapters from dynasty-scans.com"""
    category = "dynastyscans"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?dynasty-scans\.com/chapters/([^/]+)"]
    test = [
        ("http://dynasty-scans.com/chapters/hitoribocchi_no_oo_seikatsu_ch33", {
            "url": "63950fa1dfdef58ab842c1b9b854c5c1d650cfa0",
            "keyword": "7a950a94e76cceb63559de0826cb2d5a1dcaa48a",
        }),
        ("http://dynasty-scans.com/chapters/new_game_the_spinoff_special_13", {
            "url": "6b28c733481ac498da341e85a9eb155864491731",
            "keyword": "56ed59442b69d45ee4042d6586b30a72f55c3e12",
        }),
    ]
    url_base = "http://dynasty-scans.com/"

    def __init__(self, match):
        Extractor.__init__(self)
        self.chaptername = match.group(1)

    def items(self):
        page = self.request(self.url_base + "chapters/" + self.chaptername,
                            encoding="utf-8").text
        data = self.get_job_metadata(page)
        imgs = self.get_image_data(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, img in enumerate(imgs, 1):
            url = self.url_base + img["image"]
            text.nameext_from_url(url, data)
            data["page"] = num
            data["name"] = img["name"]
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        info  , pos = text.extract(page, "<h3 id='chapter-title'><b>", "</b>")
        author, pos = text.extract(page, " by ", "</a>", pos)
        date  , pos = text.extract(page, '<i class="icon-calendar"></i> ', '<', pos)
        match = re.match(
            r"(?:<a [^>]+>)?([^<]+)(?:</a>)?(?: ch(\d+))?(?:: (.+))?",
            info
        )
        return {
            "category": self.category,
            "manga": text.unescape(match.group(1)),
            "chapter": match.group(2) or "",
            "title": text.unescape(match.group(3) or ""),
            "author": text.remove_html(author),
            "date": date,
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_data(page):
        """Extract list of all image-urls for a manga chapter"""
        data = text.extract(page, "var pages = ", ";\n")[0]
        return json.loads(data)
