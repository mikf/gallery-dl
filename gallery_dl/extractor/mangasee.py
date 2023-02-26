# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangasee123.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util


class MangaseeBase():
    category = "mangasee"
    browser = "firefox"
    root = "https://mangasee123.com"

    @staticmethod
    def _transform_chapter(data):
        chapter = data["Chapter"]
        return {
            "title"   : data["ChapterName"] or "",
            "index"   : chapter[0],
            "chapter" : int(chapter[1:-1]),
            "chapter_minor": "" if chapter[-1] == "0" else "." + chapter[-1],
            "chapter_string": chapter,
            "lang"    : "en",
            "language": "English",
            "date"    : text.parse_datetime(
                data["Date"], "%Y-%m-%d %H:%M:%S"),
        }


class MangaseeChapterExtractor(MangaseeBase, ChapterExtractor):
    pattern = (r"(?:https?://)?(mangasee123|manga4life)\.com"
               r"(/read-online/[^/?#]+\.html)")
    test = (
        (("https://mangasee123.com/read-online"
          "/Tokyo-Innocent-chapter-4.5-page-1.html"), {
            "pattern": r"https://[^/]+/manga/Tokyo-Innocent/0004\.5-00\d\.png",
            "count": 8,
            "keyword": {
                "author": ["NARUMI Naru"],
                "chapter": 4,
                "chapter_minor": ".5",
                "chapter_string": "100045",
                "count": 8,
                "date": "dt:2020-01-20 21:52:53",
                "extension": "png",
                "filename": r"re:0004\.5-00\d",
                "genre": ["Comedy", "Fantasy", "Harem", "Romance", "Shounen",
                          "Supernatural"],
                "index": "1",
                "lang": "en",
                "language": "English",
                "manga": "Tokyo Innocent",
                "page": int,
                "title": "",
            },
        }),
        (("https://manga4life.com/read-online"
          "/One-Piece-chapter-1063-page-1.html"), {
            "pattern": r"https://[^/]+/manga/One-Piece/1063-0\d\d\.png",
            "count": 13,
            "keyword": {
                "author": ["ODA Eiichiro"],
                "chapter": 1063,
                "chapter_minor": "",
                "chapter_string": "110630",
                "count": 13,
                "date": "dt:2022-10-16 17:32:54",
                "extension": "png",
                "filename": r"re:1063-0\d\d",
                "genre": ["Action", "Adventure", "Comedy", "Drama", "Fantasy",
                          "Shounen"],
                "index": "1",
                "lang": "en",
                "language": "English",
                "manga": "One Piece",
                "page": int,
                "title": "",
            },
        }),
    )

    def __init__(self, match):
        if match.group(1) == "manga4life":
            self.category = "mangalife"
            self.root = "https://manga4life.com"
        ChapterExtractor.__init__(self, match, self.root + match.group(2))
        self.session.headers["Referer"] = self.gallery_url

        domain = self.root.rpartition("/")[2]
        cookies = self.session.cookies
        if not cookies.get("PHPSESSID", domain=domain):
            cookies.set("PHPSESSID", util.generate_token(13), domain=domain)

    def metadata(self, page):
        extr = text.extract_from(page)
        author = util.json_loads(extr('"author":', '],') + "]")
        genre = util.json_loads(extr('"genre":', '],') + "]")
        self.chapter = data = util.json_loads(extr("vm.CurChapter =", ";\r\n"))
        self.domain = extr('vm.CurPathName = "', '"')
        self.slug = extr('vm.IndexName = "', '"')

        data = self._transform_chapter(data)
        data["manga"] = text.unescape(extr('vm.SeriesName = "', '"'))
        data["author"] = author
        data["genre"] = genre
        return data

    def images(self, page):
        chapter = self.chapter["Chapter"][1:]
        if chapter[-1] == "0":
            chapter = chapter[:-1]
        else:
            chapter = chapter[:-1] + "." + chapter[-1]

        base = "https://{}/manga/{}/".format(self.domain, self.slug)
        if self.chapter["Directory"]:
            base += self.chapter["Directory"] + "/"
        base += chapter + "-"

        return [
            ("{}{:>03}.png".format(base, i), None)
            for i in range(1, int(self.chapter["Page"]) + 1)
        ]


class MangaseeMangaExtractor(MangaseeBase, MangaExtractor):
    chapterclass = MangaseeChapterExtractor
    pattern = r"(?:https?://)?(mangasee123|manga4life)\.com(/manga/[^/?#]+)"
    test = (
        (("https://mangasee123.com/manga"
          "/Nakamura-Koedo-To-Daizu-Keisuke-Wa-Umaku-Ikanai"), {
            "pattern": MangaseeChapterExtractor.pattern,
            "count": ">= 17",
            "keyword": {
                "author": ["TAKASE Masaya"],
                "chapter": int,
                "chapter_minor": r"re:^|\.5$",
                "chapter_string": r"re:100\d\d\d",
                "date": "type:datetime",
                "genre": ["Comedy", "Romance", "School Life", "Shounen",
                          "Slice of Life"],
                "index": "1",
                "lang": "en",
                "language": "English",
                "manga": "Nakamura-Koedo-To-Daizu-Keisuke-Wa-Umaku-Ikanai",
                "title": "",
            },
        }),
        ("https://manga4life.com/manga/Ano-Musume-Ni-Kiss-To-Shirayuri-O", {
            "pattern": MangaseeChapterExtractor.pattern,
            "count": ">= 50",
            "keyword": {
                "author": ["Canno"],
                "chapter": int,
                "chapter_minor": r"re:^|\.5$",
                "chapter_string": r"re:100\d\d\d",
                "date": "type:datetime",
                "genre": ["Comedy", "Romance", "School Life", "Seinen",
                          "Shoujo Ai"],
                "index": "1",
                "lang": "en",
                "language": "English",
                "manga": "Ano-Musume-Ni-Kiss-To-Shirayuri-O",
                "title": ""
            },
        }),
    )

    def __init__(self, match):
        if match.group(1) == "manga4life":
            self.category = "mangalife"
            self.root = "https://manga4life.com"
        MangaExtractor.__init__(self, match, self.root + match.group(2))

    def chapters(self, page):
        extr = text.extract_from(page)
        author = util.json_loads(extr('"author":', '],') + "]")
        genre = util.json_loads(extr('"genre":', '],') + "]")
        slug = extr('vm.IndexName = "', '"')
        chapters = util.json_loads(extr("vm.Chapters = ", ";\r\n"))

        result = []
        for data in map(self._transform_chapter, chapters):
            url = "{}/read-online/{}-chapter-{}{}".format(
                self.root, slug, data["chapter"], data["chapter_minor"])
            if data["index"] != "1":
                url += "-index-" + data["index"]
            url += "-page-1.html"

            data["manga"] = slug
            data["author"] = author
            data["genre"] = genre
            result.append((url, data))
        return result
