# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://mangapark.me/"""

from .common import Extractor, Message
from .. import text

class MangaparkMangaExtractor(Extractor):
    """Extractor for mangas from mangapark.me"""
    category = "mangapark"
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?mangapark\.me/manga/([^/]+)$"]
    test = [("http://mangapark.me/manga/mushishi", {
        "url": "9902e342af71af19a5ac20fcd01950b165acf119",
    })]
    url_base = "http://mangapark.me"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url_title = match.group(1)

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, self.url_base + chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request(self.url_base + "/manga/" + self.url_title).text
        needle = '<a class="ch sts sts_1" target="_blank" href="'
        pos = page.index('<div id="list" class="book-list">')
        return reversed(list(
            text.extract_iter(page, needle, '"', pos)
        ))


class MangaparkChapterExtractor(Extractor):
    """Extractor for manga-chapters from mangapark.me"""
    category = "mangapark"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{chapter-minor}"]
    filename_fmt = "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?mangapark\.me/manga/"
                r"([^/]+/s(\d+)(?:/v(\d+))?/c(\d+)(?:(\.\d+)|/e(\d+))?)")]
    test = [
        ("http://mangapark.me/manga/ad-astra-per-aspera-hata-kenjirou/s1/c1.2/1", {
            "url": "25d998a70df1fa559afc189ebd17df300b54dc28",
            "keyword": "40d60961d7aaf24454d2ab23fbc83f4c55cd4174",
        }),
        ("http://mangapark.me/manga/gekkan-shoujo-nozaki-kun/s2/c70/e2/1", {
            "url": "8534c8286a18c4db47606f84a4df9f1a42bab291",
            "keyword": "f96962442cdd5bc957603831c695159d974b7b93",
        })
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.part    = match.group(1)
        self.version = match.group(2)
        self.volume  = match.group(3)
        self.chapter = match.group(4)
        self.chminor = match.group(5) or "." + match.group(6)

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
        """Collect metadata for extractor-job"""
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

    @staticmethod
    def get_images(page):
        """Collect image-urls, -widths and -heights"""
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
