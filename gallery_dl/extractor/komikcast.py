# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://komikcast.li/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = (r"(?:https?://)?(?:www\.)?"
                r"komikcast\d*\.(?:l(?:i|a|ol)|com|cz|site|mo?e)")


class KomikcastBase():
    """Base class for komikcast extractors"""
    category = "komikcast"
    root = "https://komikcast.li"

    def parse_chapter_string(self, chapter_string, data=None):
        """Parse 'chapter_string' value and add its info to 'data'"""
        if data is None:
            data = {}

        pattern = text.re(r"(?:(.*) Chapter )?0*(\d+)([^ ]*)(?: (?:- )?(.+))?")
        match = pattern.match(text.unescape(chapter_string))
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
    """Extractor for komikcast manga chapters"""
    pattern = rf"{BASE_PATTERN}(/chapter/[^/?#]+/)"
    example = "https://komikcast.li/chapter/TITLE/"

    def metadata(self, page):
        info = text.extr(page, "<title>", " - Komikcast<")
        return self.parse_chapter_string(info)

    def images(self, page):
        readerarea = text.extr(
            page, '<div class="main-reading-area', '</div')
        pattern = text.re(r"<img[^>]* src=[\"']([^\"']+)")
        return [
            (text.unescape(url), None)
            for url in pattern.findall(readerarea)
        ]


class KomikcastMangaExtractor(KomikcastBase, MangaExtractor):
    """Extractor for komikcast manga"""
    chapterclass = KomikcastChapterExtractor
    pattern = rf"{BASE_PATTERN}(/(?:komik/)?[^/?#]+/?)$"
    example = "https://komikcast.li/komik/TITLE"

    def chapters(self, page):
        results = []
        data = self.metadata(page)

        for item in text.extract_iter(
                page, '<a class="chapter-link-item" href="', '</a'):
            url, _, chapter = item.rpartition('">Chapter')
            chapter, sep, minor = chapter.strip().partition(".")
            data["chapter"] = text.parse_int(chapter)
            data["chapter_minor"] = sep + minor
            results.append((url, data.copy()))
        return results

    def metadata(self, page):
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
