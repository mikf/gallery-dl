# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangapark.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text


class MangaparkExtractor():
    """Base class for mangapark extractors"""
    category = "mangapark"
    root_fmt = "https://mangapark.{}"

    @staticmethod
    def parse_chapter_path(path, data):
        """Get volume/chapter information from url-path of a chapter"""
        data["volume"], data["chapter_minor"] = 0, ""
        for part in path.split("/")[3:]:
            key, value = part[0], part[1:]
            if key == "s":
                data["version"] = text.parse_int(value)
            elif key == "v":
                data["volume"] = text.parse_int(value)
            elif key == "c":
                chapter, dot, minor = value.partition(".")
                data["chapter"] = text.parse_int(chapter)
                data["chapter_minor"] = dot + minor
            elif key == "e":
                data["chapter_minor"] = "v" + value


class MangaparkMangaExtractor(MangaparkExtractor, MangaExtractor):
    """Extractor for manga from mangapark.me"""
    pattern = [r"(?:https?://)?(?:www\.)?mangapark\.(me|net|com)"
               r"(/manga/[^/?&#]+)/?$"]
    test = [
        ("https://mangapark.me/manga/aria", {
            "url": "4cb5606530b4eeacde7a4c9fd38296eb6ff46563",
            "keyword": "e87ab8e7ad2571bbe587881e7fd422e8f582f818",
        }),
        ("https://mangapark.net/manga/aria", None),
        ("https://mangapark.com/manga/aria", None),
    ]

    def __init__(self, match):
        self.root = self.root_fmt.format(match.group(1))
        MangaExtractor.__init__(self, match, self.root + match.group(2))

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
            data["count"] = text.parse_int(count)
            results.append((self.root + path, data.copy()))


class MangaparkChapterExtractor(MangaparkExtractor, ChapterExtractor):
    """Extractor for manga-chapters from mangapark.me"""
    pattern = [(r"(?:https?://)?(?:www\.)?mangapark\.(me|net|com)"
                r"(/manga/[^/]+/s\d+(?:/v\d+)?/c\d+[^/]*(?:/e\d+)?)")]
    test = [
        ("https://mangapark.me/manga/gosu/s2/c55", {
            "count": 50,
            "keyword": "5454f37e6ca4113c5639c9bdad5185ccdce4bb10",
        }),
        (("https://mangapark.me/manga/"
          "ad-astra-per-aspera-hata-kenjirou/s5/c1.2"), {
            "count": 40,
            "keyword": "f7f7fb1ca8b26a59a47d8ec60c5eaaf69a43a3f6",
        }),
        ("https://mangapark.me/manga/gekkan-shoujo-nozaki-kun/s2/c70/e2/1", {
            "count": 15,
            "keyword": "e6ef5192c8484d598bc834add4a56ee067e23b73",
        }),
        ("https://mangapark.net/manga/gosu/s2/c55", None),
        ("https://mangapark.com/manga/gosu/s2/c55", None),
    ]

    def __init__(self, match):
        tld, self.path = match.groups()
        self.root = self.root_fmt.format(tld)
        url = self.root + self.path + "?zoom=2"
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
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
        data["count"] = text.parse_int(data["count"])
        return data

    def get_images(self, page):
        pos = 0
        while True:
            url, pos = text.extract(page, ' target="_blank" href="', '"', pos)
            if not url:
                return
            width , pos = text.extract(page, ' width="', '"', pos)
            height, pos = text.extract(page, ' _heighth="', '"', pos)
            yield text.urljoin(self.root, url), {
                "width": width,
                "height": height,
            }
