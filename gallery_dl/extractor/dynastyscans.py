# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://dynasty-scans.com/"""

from .common import ChapterExtractor
from .. import text
import re
import json


class DynastyscansChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from dynasty-scans.com"""
    category = "dynastyscans"
    pattern = [r"(?:https?://)?(?:www\.)?dynasty-scans\.com/chapters/([^/]+)"]
    test = [
        (("http://dynasty-scans.com/chapters/"
          "hitoribocchi_no_oo_seikatsu_ch33"), {
            "url": "dce64e8c504118f1ab4135c00245ea12413896cb",
            "keyword": "ec5c56bbd5c97aa521d00f2598bba4663fb8ab9f",
        }),
        (("http://dynasty-scans.com/chapters/"
          "new_game_the_spinoff_special_13"), {
            "url": "dbe5bbb74da2edcfb1832895a484e2a40bc8b538",
            "keyword": "1208a102d9a1bb0b0c740a67996d9b26a9357b64",
        }),
    ]
    root = "https://dynasty-scans.com"

    def __init__(self, match):
        self.chaptername = match.group(1)
        url = self.root + "/chapters/" + self.chaptername
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        info  , pos = text.extract(page, "<h3 id='chapter-title'><b>", "</b>")
        author, pos = text.extract(page, " by ", "</a>", pos)
        group , pos = text.extract(page, '"icon-print"></i> ', '</span>', pos)
        date  , pos = text.extract(page, '"icon-calendar"></i> ', '<', pos)

        match = re.match(
            (r"(?:<a[^>]*>)?([^<]+)(?:</a>)?"  # manga name
             r"(?: ch(\d+)([^:<]*))?"  # chapter info
             r"(?:: (.+))?"),  # title
            info
        )

        return {
            "manga": text.unescape(match.group(1)),
            "chapter": text.parse_int(match.group(2)),
            "chapter_minor": match.group(3) or "",
            "title": text.unescape(match.group(4) or ""),
            "author": text.remove_html(author),
            "group": (text.remove_html(group) or
                      text.extract(group, ' alt="', '"')[0] or ""),
            "date": date,
            "lang": "en",
            "language": "English",
        }

    def get_images(self, page):
        """Extract list of all image-urls for a manga chapter"""
        data = text.extract(page, "var pages = ", ";\n")[0]
        return [
            (self.root + img["image"], None)
            for img in json.loads(data)
        ]
