# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
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
    directory_fmt = ["{category}", "{manga}",
                     "c{chapter:>03}{chapter-minor} - {title}"]
    filename_fmt = ("{manga}_c{chapter:>03}{chapter-minor}_"
                    "{page:>03}.{extension}")
    pattern = [(r"(?:https?://)?(?:www\.)?mangapark\.me/manga/"
                r"([^/]+/s(\d+)(?:/v([^/]+))?/c(\d+)(?:([^/]+)|/e(\d+))?)")]
    test = [
        ("http://mangapark.me/manga/gosu/s2/c55", {
            "url": "fefe84492d9118de5962563fbecb9362051c52d5",
            "keyword": "652b38c40bdfb5592456b6e7524a3acfdef9fae6",
        }),
        (("http://mangapark.me/manga/"
          "ad-astra-per-aspera-hata-kenjirou/s1/c1.2"), {
            "url": "64b47f9837d50c3e57793ff6703d840ef7808c52",
            "keyword": "f28eb26b4966bebda0e761f241c2dd49e505ce13",
        }),
        ("http://mangapark.me/manga/gekkan-shoujo-nozaki-kun/s2/c70/e2/1", {
            "url": "f8915e25895d4b336892f8a6bd27d26cdb337045",
            "keyword": "34aa6ca3bdf5078f839cbf68ff68e39728cf248b",
        })
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.part = match.group(1)
        self.version = match.group(2)
        self.volume = match.group(3)
        self.chapter = match.group(4)
        try:
            self.chminor = match.group(5) or "v" + match.group(6)
        except TypeError:
            self.chminor = ""

    def items(self):
        page = self.request("http://mangapark.me/manga/" + self.part +
                            "?zoom=2").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images(page):
            data.update(image)
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
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
            ("title"     , "</a>", "<"),
            (None        , 'target="_blank" href="', ''),
            ("count"     , 'page 1">1 / ', '<'),
        ), values=data)[0]
        data["manga"], data["type"] = data["manga"].rsplit(" ", maxsplit=1)
        data["manga"] = text.unescape(data["manga"])
        pos = data["title"].find(": ")
        data["title"] = data["title"][pos+2:] if pos != -1 else ""
        return data

    @staticmethod
    def get_images(page):
        """Collect image-urls, -widths and -heights"""
        pos = 0
        num = 0
        while True:
            url, pos = text.extract(page, ' target="_blank" href="', '"', pos)
            if not url:
                return
            num += 1
            width , pos = text.extract(page, ' width="', '"', pos)
            height, pos = text.extract(page, ' _heighth="', '"', pos)
            yield url, {
                "page": num,
                "width": width,
                "height": height,
            }
