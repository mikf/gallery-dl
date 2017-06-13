# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://mangapark.me/"""

from .common import Extractor, MangaExtractor, Message
from .. import text


class MangaparkMangaExtractor(MangaExtractor):
    """Extractor for manga from mangapark.me"""
    category = "mangapark"
    pattern = [r"(?:https?://)?(?:www\.)?(mangapark\.me/manga/[^/]+)$"]
    root = "http://mangapark.me"
    test = [("http://mangapark.me/manga/mushishi", {
        "url": "9902e342af71af19a5ac20fcd01950b165acf119",
    })]

    def chapter_paths(self, page):
        needle = '<a class="ch sts sts_1" target="_blank" href="'
        pos = page.index('<div id="list" class="book-list">')
        return text.extract_iter(page, needle, '"', pos)


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
            "keyword": "bd97ca24ef344b44292910384215ef3f1005ea2e",
        }),
        (("http://mangapark.me/manga/"
          "ad-astra-per-aspera-hata-kenjirou/s1/c1.2"), {
            "keyword": "6e56986610cb2da9917d0d9d3217d700fbc48665",
        }),
        ("http://mangapark.me/manga/gekkan-shoujo-nozaki-kun/s2/c70/e2/1", {
            "keyword": "46a332caa65ef646c9405f69947c27f0dbc5430e",
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
