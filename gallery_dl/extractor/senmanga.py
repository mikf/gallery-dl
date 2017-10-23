# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from from http://raw.senmanga.com/"""

from .common import Extractor, Message
from .. import text, util


class SenmangaChapterExtractor(Extractor):
    """Extractor for manga-chapters from raw.senmanga.com"""
    category = "senmanga"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "{chapter_string}"]
    filename_fmt = "{manga}_{chapter_string}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?raw\.senmanga\.com/([^/]+/[^/]+)"]
    test = [
        ("http://raw.senmanga.com/Bokura-wa-Minna-Kawaisou/37A/1", {
            "url": "32d88382fcad66859d089cd9a61249f375492ec5",
            "keyword": "705d941a150765edb33cd2707074bd703a93788c",
            "content": "a791dda85ac0d37e3b36d754560cbb65b8dab5b9",
        }),
        ("http://raw.senmanga.com/Love-Lab/2016-03/1", {
            "url": "d4f37c7347e56a09f9679d63c1f24cd32621d0b8",
            "keyword": "4e72e4ade57671ad0af9c8d81feeff4259d5bbec",
        }),
    ]
    url_base = "http://raw.senmanga.com"

    def __init__(self, match):
        Extractor.__init__(self)
        part = match.group(1)
        self.chapter_url = "{}/{}/".format(self.url_base, part)
        self.img_url = "{}/viewer/{}/".format(self.url_base, part)
        self.session.headers["Referer"] = self.chapter_url
        self.session.headers["User-Agent"] = "Mozilla 5.0"

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"] in range(1, data["count"]+1):
            data["extension"] = None
            yield Message.Url, self.img_url + str(data["page"]), data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        page = self.request(self.chapter_url).text
        title, pos = text.extract(page, '<title>', '</title>')
        count, pos = text.extract(page, '</select> of ', ' ', pos)
        manga, pos = text.extract(title, '| Raw | ', '  |  Chapter ')
        chapter, pos = text.extract(title, '', ' |  Page ', pos)
        return {
            "manga": text.unescape(manga.replace("-", " ")),
            "chapter_string": chapter,
            "count": util.safe_int(count),
            "lang": "jp",
            "language": "Japanese",
        }
