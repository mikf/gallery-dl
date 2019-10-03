# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://komikcast.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re


class KomikcastBase():
    """Base class for komikcast extractors"""
    category = "komikcast"
    root = "https://komikcast.com"

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
        if title and title.lower() != "bahasa indonesia":
            data["title"] = title.strip()
        else:
            data["title"] = ""
        data["chapter"] = text.parse_int(chapter)
        data["lang"] = "id"
        data["language"] = "Indonesian"

        return data


class KomikcastChapterExtractor(KomikcastBase, ChapterExtractor):
    """Extractor for manga-chapters from komikcast.com"""
    pattern = r"(?:https?://)?(?:www\.)?komikcast\.com(/chapter/[^/?&#]+/)"
    test = (
        (("https://komikcast.com/chapter/"
          "apotheosis-chapter-02-2-bahasa-indonesia/"), {
            "url": "f6b43fbc027697749b3ea1c14931c83f878d7936",
            "keyword": "f3938e1aff9ad1f302f52447e9781b21f6da26d4",
        }),
        (("https://komikcast.com/chapter/"
          "tonari-no-kashiwagi-san-chapter-18b/"), {
            "url": "aff90dd21dbb945a726778b10bdef522af7c42fe",
            "keyword": "19b5783864c4299913de436513b124b028b557c1",
        }),
        (("https://komikcast.com/chapter/090-eko-to-issho-chapter-1/"), {
            "url": "cda104a32ea2b06b3d6b096726622f519ed1fa33",
        }),
    )

    def metadata(self, page):
        info = text.extract(page, '<b>', "</b>")[0]
        return self.parse_chapter_string(info)

    @staticmethod
    def images(page):
        readerarea = text.extract(
            page, '<div id="readerarea">', '<div class="navig">')[0]
        return [
            (text.unescape(url), None)
            for url in re.findall(r"<img[^>]* src=[\"']([^\"']+)", readerarea)
            if "/Banner-" not in url and "/WM-Sampingan." not in url
        ]


class KomikcastMangaExtractor(KomikcastBase, MangaExtractor):
    """Extractor for manga from komikcast.com"""
    chapterclass = KomikcastChapterExtractor
    pattern = (r"(?:https?://)?(?:www\.)?komikcast\.com"
               r"(/(?:komik/)?[^/?&#]+)/?$")
    test = (
        ("https://komikcast.com/komik/090-eko-to-issho/", {
            "url": "dc798d107697d1f2309b14ca24ca9dba30c6600f",
            "keyword": "837a7e96867344ff59d840771c04c20dc46c0ab1",
        }),
        ("https://komikcast.com/tonari-no-kashiwagi-san/"),
    )

    def chapters(self, page):
        results = []
        data = self.metadata(page)

        for item in text.extract_iter(
                page, '<span class="leftoff"><a href="', '</a>'):
            url, _, chapter_string = item.rpartition('">Chapter ')
            self.parse_chapter_string(chapter_string, data)
            results.append((url, data.copy()))
        return results

    @staticmethod
    def metadata(page):
        """Return a dict with general metadata"""
        manga , pos = text.extract(page, "<title>" , "</title>")
        genres, pos = text.extract(page, ">Genres:", "</span>", pos)
        author, pos = text.extract(page, ">Author:", "</span>", pos)
        mtype , pos = text.extract(page, ">Type:"  , "</span>", pos)

        return {
            "manga": text.unescape(manga[:-12]),
            "author": text.remove_html(author),
            "genres": text.split_html(genres)[::2],
            "type": text.remove_html(mtype),
        }
