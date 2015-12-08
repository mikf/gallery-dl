# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://mangapark.me/"""

from .common import Extractor, Message
from .. import text
import re

class MangaparkChapterExtractor(Extractor):
    """Extract a single manga-chapter from mangapark"""
    category = "mangapark"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{chapter-minor}"]
    filename_fmt = "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?mangapark\.me/manga/([^/]+/s(\d+)(?:/v(\d+))?/c(\d+)(\.\d+)?)"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.part, self.version, self.volume, self.chapter, self.chminor = match.groups()

    def items(self):
        page = self.request("http://mangapark.me/manga/" + self.part + "?zoom=2").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, image in enumerate(self.get_images(page), 1):
            data.update(image)
            data["page"] = num
            yield Message.Url, data["url"], text.nameext_from_url(data["url"], data)

    def get_job_metadata(self, page):
        data = {
            "category": self.category,
            "version": self.version,
            "volume": self.volume or "",
            "chapter": self.chapter,
            "chapter-minor": self.chminor or "",
            "lang": "en",
            "language": "English",
        }
        data = text.extract_all(page, (
            ("manga-id"  , "var _manga_id = '", "'"),
            ("chapter-id", "var _book_id = '", "'"),
            ("manga"     , "<h2>", "</h2>"),
            (None        , 'target="_blank" href="', ''),
            ("count"     , 'page 1">1 / ', '<'),
        ), values=data)[0]
        pos = data["manga"].rfind(" ")
        data["manga"] = data["manga"][:pos]
        return data

    def get_images(self, page):
        pos = 0
        while True:
            url   , pos = text.extract(page, ' target="_blank" href="', '"', pos)
            if not url:
                return
            width , pos = text.extract(page, ' width="', '"', pos)
            height, pos = text.extract(page, ' _heighth="', '"', pos)
            yield {
                "url": url,
                "width": width,
                "height": height,
            }
