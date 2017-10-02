# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://mangapark.me/"""

from .common import Extractor, MangaExtractor, Message
from .. import text, util


class MangaparkExtractor(Extractor):
    """Base class for mangapark extractors"""
    category = "mangapark"
    root = "http://mangapark.me"

    @staticmethod
    def parse_chapter_path(path, data):
        """Get volume/chapter information from url-path of a chapter"""
        data["volume"], data["chapter_minor"] = 0, ""
        for part in path.split("/")[3:]:
            key, value = part[0], part[1:]
            if key == "s":
                data["version"] = util.safe_int(value)
            elif key == "v":
                data["volume"] = util.safe_int(value)
            elif key == "c":
                chapter, dot, minor = value.partition(".")
                data["chapter"] = util.safe_int(chapter)
                data["chapter_minor"] = dot + minor
            elif key == "e":
                data["chapter_minor"] = "v" + value


class MangaparkMangaExtractor(MangaparkExtractor, MangaExtractor):
    """Extractor for manga from mangapark.me"""
    pattern = [r"(?:https?://)?(?:www\.)?(mangapark\.me/manga/[^/]+)/?$"]
    test = [("http://mangapark.me/manga/mushishi", {
        "url": "724a0e3de636bb6130973d9596c980c7e12d3535",
        "keyword": "8299b696df873de47dc3bd043bb51edd8053216a",
    })]

    def chapters(self, page):
        results = []
        data = {"lang": "en", "language": "English"}
        data["manga"] = text.unescape(
            text.extract(page, '<title>', ' Manga - Read ')[0])

        pos = page.index('<div id="list" class="book-list">')
        while True:
            test, pos = text.extract(page, '<a class="ch sts sts_', '', pos)
            if test is None:
                return results

            path , pos = text.extract(page, 'href="', '"', pos)
            title, pos = text.extract(page, '</a>', '</span>', pos)
            date , pos = text.extract(page, '<i>', '</i>', pos)
            count, pos = text.extract(page, '\tof ', ' ', pos)

            self.parse_chapter_path(path, data)
            data["title"] = title[3:].strip()
            data["date"] = date
            data["count"] = util.safe_int(count)
            results.append((self.root + path, data.copy()))


class MangaparkChapterExtractor(MangaparkExtractor):
    """Extractor for manga-chapters from mangapark.me"""
    subcategory = "chapter"
    directory_fmt = [
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}{title:?: //}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    pattern = [(r"(?:https?://)?(?:www\.)?mangapark\.me(/manga/[^/]+"
                r"/s\d+(?:/v\d+)?/c\d+[^/]*(?:/e\d+)?)")]
    test = [
        ("http://mangapark.me/manga/gosu/s2/c55", {
            "count": 50,
            "keyword": "72ac1714b492b021a1fe26d9271ed132d51a930e",
        }),
        (("http://mangapark.me/manga/"
          "ad-astra-per-aspera-hata-kenjirou/s1/c1.2"), {
            "count": 40,
            "keyword": "0ac6a028f6479b2ecfe7b2d014074a0aea027e90",
        }),
        ("http://mangapark.me/manga/gekkan-shoujo-nozaki-kun/s2/c70/e2/1", {
            "count": 15,
            "keyword": "5760c0a5efd1ffe24468cfaac5b41d048af36360",
        }),
    ]

    def __init__(self, match):
        MangaparkExtractor.__init__(self)
        self.path = match.group(1)

    def items(self):
        page = self.request(self.root + self.path + "?zoom=2").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images(page):
            data.update(image)
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {"lang": "en", "language": "English"}
        self.parse_chapter_path(self.path, data)
        text.extract_all(page, (
            ("manga_id"  , "var _manga_id = '", "'"),
            ("chapter_id", "var _book_id = '", "'"),
            ("manga"     , "<h2>", "</h2>"),
            ("title"     , "</a>", "<"),
            (None        , 'target="_blank" href="', ''),
            ("count"     , 'page 1">1 / ', '<'),
        ), values=data)
        data["manga"], _, data["type"] = data["manga"].rpartition(" ")
        data["manga"] = text.unescape(data["manga"])
        data["title"] = data["title"].partition(": ")[2]
        data["count"] = util.safe_int(data["count"])
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
