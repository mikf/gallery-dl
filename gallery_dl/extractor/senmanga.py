# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from from http://raw.senmanga.com/"""

from .common import Extractor, Message
from .. import text


class SenmangaChapterExtractor(Extractor):
    """Extractor for manga-chapters from raw.senmanga.com"""
    category = "senmanga"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?raw\.senmanga\.com/([^/]+/[^/]+)"]
    test = [("http://raw.senmanga.com/Bokura-wa-Minna-Kawaisou/37A/1", {
        "url": "32d88382fcad66859d089cd9a61249f375492ec5",
        "keyword": "bd25a8d00c8507faa5cdd6146a872797486fbf93",
        "content": "a791dda85ac0d37e3b36d754560cbb65b8dab5b9",
    })]
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
        yield Message.Headers, self.session.headers
        for i in range(int(data["count"])):
            page = str(i+1)
            data["page"] = page
            data["extension"] = ""
            yield Message.Url, self.img_url + page, data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        page = self.request(self.chapter_url).text
        title, pos = text.extract(page, '<title>', '</title>')
        count, pos = text.extract(page, '</select> of ', ' ', pos)
        manga, pos = text.extract(title, '| Raw | ', '  |  Chapter ')
        chapter, pos = text.extract(title, '', ' |  Page ', pos)
        return {
            "manga": text.unescape(manga.replace("-", " ")),
            "chapter": chapter,
            "count": count,
            "lang": "jp",
            "language": "Japanese",
        }
