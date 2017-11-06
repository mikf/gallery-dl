# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://dynasty-scans.com/"""

from .common import Extractor, Message
from .. import text, util
import re
import json


class DynastyscansChapterExtractor(Extractor):
    """Extractor for manga-chapters from dynasty-scans.com"""
    category = "dynastyscans"
    subcategory = "chapter"
    directory_fmt = [
        "{category}", "{manga}", "c{chapter:>03}{chapter_minor}{title:?: //}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    pattern = [r"(?:https?://)?(?:www\.)?dynasty-scans\.com/chapters/([^/]+)"]
    test = [
        (("http://dynasty-scans.com/chapters/"
          "hitoribocchi_no_oo_seikatsu_ch33"), {
            "url": "dce64e8c504118f1ab4135c00245ea12413896cb",
            "keyword": "fb2f470b995df5b301ccede31ed9829a010236db",
        }),
        (("http://dynasty-scans.com/chapters/"
          "new_game_the_spinoff_special_13"), {
            "url": "dbe5bbb74da2edcfb1832895a484e2a40bc8b538",
            "keyword": "281bbe0fb74b812ced595619ca5876983490dc0e",
        }),
    ]
    root = "https://dynasty-scans.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.chaptername = match.group(1)

    def items(self):
        page = self.request(self.root + "/chapters/" + self.chaptername,
                            encoding="utf-8").text
        data = self.get_job_metadata(page)
        imgs = self.get_image_data(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], img in enumerate(imgs, 1):
            url = self.root + img["image"]
            text.nameext_from_url(url, data)
            data["name"] = img["name"]
            yield Message.Url, url, data

    def get_job_metadata(self, page):
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
            "chapter": util.safe_int(match.group(2)),
            "chapter_minor": match.group(3) or "",
            "title": text.unescape(match.group(4) or ""),
            "author": text.remove_html(author),
            "group": (text.remove_html(group) or
                      text.extract(group, ' alt="', '"')[0] or ""),
            "date": date,
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_data(page):
        """Extract list of all image-urls for a manga chapter"""
        data = text.extract(page, "var pages = ", ";\n")[0]
        return json.loads(data)
