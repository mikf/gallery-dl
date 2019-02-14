# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangapark.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, exception
import json


class MangaparkBase():
    """Base class for mangapark extractors"""
    category = "mangapark"
    root_fmt = "https://mangapark.{}"

    @staticmethod
    def parse_chapter_path(path, data):
        """Get volume/chapter information from url-path of a chapter"""
        data["volume"], data["chapter_minor"] = 0, ""
        for part in path.split("/")[1:]:
            key, value = part[0], part[1:]
            if key == "c":
                chapter, dot, minor = value.partition(".")
                data["chapter"] = text.parse_int(chapter)
                data["chapter_minor"] = dot + minor
            elif key == "i":
                data["chapter_id"] = text.parse_int(value)
            elif key == "v":
                data["volume"] = text.parse_int(value)
            elif key == "s":
                data["stream"] = text.parse_int(value)
            elif key == "e":
                data["chapter_minor"] = "v" + value


class MangaparkChapterExtractor(MangaparkBase, ChapterExtractor):
    """Extractor for manga-chapters from mangapark.me"""
    pattern = (r"(?:https?://)?(?:www\.)?mangapark\.(me|net|com)"
               r"/manga/([^?&#]+/i\d+)")
    test = (
        ("https://mangapark.me/manga/gosu/i811615/c55/1", {
            "count": 50,
            "keyword": "373d678048d29492f9763743ccaa9b6d840f17cf",
        }),
        (("https://mangapark.me/manga"
          "/ad-astra-per-aspera-hata-kenjirou/i662054/c001.2/1"), {
            "count": 40,
            "keyword": "8e9cce4ed0e25d12a45e02f840d6f32ef838e257",
        }),
        ("https://mangapark.me/manga/gekkan-shoujo-nozaki-kun/i655476/c70/1", {
            "count": 15,
            "keyword": "19f730617074d65f91c0781f429de324890925bf",
        }),
        ("https://mangapark.net/manga/gosu/i811615/c55/1"),
        ("https://mangapark.com/manga/gosu/i811615/c55/1"),
    )

    def __init__(self, match):
        tld, self.path = match.groups()
        self.root = self.root_fmt.format(tld)
        url = "{}/manga/{}?zoom=2".format(self.root, self.path)
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        data = text.extract_all(page, (
            ("manga_id"  , "var _manga_id = '", "'"),
            ("chapter_id", "var _book_id = '", "'"),
            ("stream"    , "var _stream = '", "'"),
            ("path"      , "var _book_link = '", "'"),
            ("manga"     , "<h2>", "</h2>"),
            ("title"     , "</a>", "<"),
        ), values={"lang": "en", "language": "English"})[0]

        if not data["path"]:
            raise exception.NotFoundError("chapter")
        self.parse_chapter_path(data["path"], data)

        data["manga"], _, data["type"] = data["manga"].rpartition(" ")
        data["manga"] = text.unescape(data["manga"])
        data["title"] = data["title"].partition(": ")[2]
        for key in ("manga_id", "chapter_id", "stream"):
            data[key] = text.parse_int(data[key])

        return data

    def images(self, page):
        data = json.loads(text.extract(
            page, "var _load_pages =", ";")[0] or "[]")
        return [
            (text.urljoin(self.root, item["u"]), {
                "width": text.parse_int(item["w"]),
                "height": text.parse_int(item["h"]),
            })
            for item in data
        ]


class MangaparkMangaExtractor(MangaparkBase, MangaExtractor):
    """Extractor for manga from mangapark.me"""
    chapterclass = MangaparkChapterExtractor
    pattern = (r"(?:https?://)?(?:www\.)?mangapark\.(me|net|com)"
               r"(/manga/[^/?&#]+)/?$")
    test = (
        ("https://mangapark.me/manga/aria", {
            "url": "a58be23ef3874fe9705b0b41dd462b67eaaafd9a",
            "keyword": "b3b5a30aa2a326bc0ca8b74c65b5ecd4bf676ebf",
        }),
        ("https://mangapark.net/manga/aria"),
        ("https://mangapark.com/manga/aria"),
    )

    def __init__(self, match):
        self.root = self.root_fmt.format(match.group(1))
        MangaExtractor.__init__(self, match, self.root + match.group(2))

    def chapters(self, page):
        results = []
        data = {"lang": "en", "language": "English"}
        data["manga"] = text.unescape(
            text.extract(page, '<title>', ' Manga - ')[0])

        for stream in page.split('<div id="stream_')[1:]:
            data["stream"] = text.parse_int(text.extract(stream, '', '"')[0])

            for chapter in text.extract_iter(stream, '<li ', '</li>'):
                path , pos = text.extract(chapter, 'href="', '"')
                title, pos = text.extract(chapter, '>: </span>', '<', pos)
                count, pos = text.extract(chapter, '  of ', ' ', pos)

                self.parse_chapter_path(path[8:], data)
                data["title"] = title.strip() if title else ""
                data["count"] = text.parse_int(count)
                results.append((self.root + path, data.copy()))

        return results
