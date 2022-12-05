# -*- coding: utf-8 -*-

# Copyright 2018-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://komikcast.site/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?komikcast\.(?:site|me|com)"


class KomikcastBase():
    """Base class for komikcast extractors"""
    category = "komikcast"
    root = "https://komikcast.site"

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
    """Extractor for manga-chapters from komikcast.site"""
    pattern = BASE_PATTERN + r"(/chapter/[^/?#]+/)"
    test = (
        (("https://komikcast.site/chapter"
          "/apotheosis-chapter-02-2-bahasa-indonesia/"), {
            "url": "f6b43fbc027697749b3ea1c14931c83f878d7936",
            "keyword": "f3938e1aff9ad1f302f52447e9781b21f6da26d4",
        }),
        (("https://komikcast.me/chapter"
          "/soul-land-ii-chapter-300-1-bahasa-indonesia/"), {
            "url": "efd00a9bd95461272d51990d7bc54b79ff3ff2e6",
            "keyword": "cb646cfed3d45105bd645ab38b2e9f7d8c436436",
        }),
    )

    def metadata(self, page):
        info = text.extr(page, "<title>", " - Komikcast<")
        return self.parse_chapter_string(info)

    @staticmethod
    def images(page):
        readerarea = text.extr(
            page, '<div class="main-reading-area', '</div')
        return [
            (text.unescape(url), None)
            for url in re.findall(r"<img[^>]* src=[\"']([^\"']+)", readerarea)
        ]


class KomikcastMangaExtractor(KomikcastBase, MangaExtractor):
    """Extractor for manga from komikcast.site"""
    chapterclass = KomikcastChapterExtractor
    pattern = BASE_PATTERN + r"(/(?:komik/)?[^/?#]+)/?$"
    test = (
        ("https://komikcast.site/komik/090-eko-to-issho/", {
            "url": "19d3d50d532e84be6280a3d61ff0fd0ca04dd6b4",
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
        manga , pos = text.extract(page, "<title>" , " - Komikcast<")
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
