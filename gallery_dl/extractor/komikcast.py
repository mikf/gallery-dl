# -*- coding: utf-8 -*-

# Copyright 2018-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://komikcast.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?komikcast\.(?:me|com)"


class KomikcastBase():
    """Base class for komikcast extractors"""
    category = "komikcast"
    root = "https://komikcast.me"

    @staticmethod
    def parse_chapter_string(chapter_string, data=None):
        """Parse 'chapter_string' value and add its info to 'data'"""
        if not data:
            data = {}

        match = re.match(
            r"(?:(.*) Chapter )?0*(\d+)([^ ]*)(?: (?:- )?(.+))?",
            text.unescape(chapter_string),
        )
        manga, chapter, data["chapter_minor"], title = match.groups()

        if manga:
            data["manga"] = manga.partition(" Chapter ")[0]
        if title and not title.lower().startswith("bahasa indonesia"):
            data["title"] = title.strip()
        else:
            data["title"] = ""
        data["chapter"] = text.parse_int(chapter)
        data["lang"] = "id"
        data["language"] = "Indonesian"

        return data


class KomikcastChapterExtractor(KomikcastBase, ChapterExtractor):
    """Extractor for manga-chapters from komikcast.me"""
    pattern = BASE_PATTERN + r"(/chapter/[^/?#]+/)"
    test = (
        (("https://komikcast.me/chapter"
          "/apotheosis-chapter-02-2-bahasa-indonesia/"), {
            "url": "74eca5c9b27b896816497f9b2d847f2a1fcfc209",
            "keyword": "f3938e1aff9ad1f302f52447e9781b21f6da26d4",
        }),
        (("https://komikcast.me/chapter"
          "/soul-land-ii-chapter-300-1-bahasa-indonesia/"), {
            "url": "243a5250e210b40d17217e83b7547cefea5638bd",
            "keyword": "cb646cfed3d45105bd645ab38b2e9f7d8c436436",
        }),
    )

    def metadata(self, page):
        info = text.extract(page, "<title>", " – Komikcast<")[0]
        return self.parse_chapter_string(info)

    @staticmethod
    def images(page):
        readerarea = text.extract(
            page, '<div class="main-reading-area', '</div')[0]
        return [
            (text.unescape(url), None)
            for url in re.findall(r"<img[^>]* src=[\"']([^\"']+)", readerarea)
        ]


class KomikcastMangaExtractor(KomikcastBase, MangaExtractor):
    """Extractor for manga from komikcast.me"""
    chapterclass = KomikcastChapterExtractor
    pattern = BASE_PATTERN + r"(/(?:komik/)?[^/?#]+)/?$"
    test = (
        ("https://komikcast.me/komik/090-eko-to-issho/", {
            "url": "08204f0a703ec5272121abcf0632ecacba1e588f",
            "keyword": "837a7e96867344ff59d840771c04c20dc46c0ab1",
        }),
        ("https://komikcast.me/tonari-no-kashiwagi-san/"),
    )

    def chapters(self, page):
        results = []
        data = self.metadata(page)

        for item in text.extract_iter(
                page, '<a class="chapter-link-item" href="', '</a'):
            url, _, chapter_string = item.rpartition('">Chapter ')
            self.parse_chapter_string(chapter_string, data)
            results.append((url, data.copy()))
        return results

    @staticmethod
    def metadata(page):
        """Return a dict with general metadata"""
        manga , pos = text.extract(page, "<title>" , " – Komikcast<")
        genres, pos = text.extract(
            page, 'class="komik_info-content-genre">', "</span>", pos)
        author, pos = text.extract(page, ">Author:", "</span>", pos)
        mtype , pos = text.extract(page, ">Type:"  , "</span>", pos)

        return {
            "manga": text.unescape(manga),
            "genres": text.split_html(genres),
            "author": text.remove_html(author),
            "type": text.remove_html(mtype),
        }
