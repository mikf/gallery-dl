# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://dynasty-scans.com/"""

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
        (("http://dynasty-scans.com/chapters/"
          "hitoribocchi_no_oo_seikatsu_ch33"), {
            "url": "ff79ea9956522a8dafd261c1fbe3c74aa8470dc5",
            "keyword": "eb837477565ee7e647d08ae0ac60c1108234cb80",
        }),
        (("http://dynasty-scans.com/chapters/"
          "new_game_the_spinoff_special_13"), {
            "url": "2cd5e04bd16f842dc884c145a44cf0c64ec27a21",
            "keyword": "93b75d0c0aaeb849c99f2225a4b97f466bc3ace9",
        }),
    ]
    url_base = "https://dynasty-scans.com/"

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
        date  , pos = text.extract(page, '"icon-calendar"></i> ', '<', pos)
        match = re.match(
            r"(?:<a [^>]+>)?([^<]+)(?:</a>)?(?: ch(\d+))?(?:: (.+))?",
            info
        )
        return {
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
