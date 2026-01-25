# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ww2.mangafreak.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:ww\d\.)?mangafreak\.me"


class MangafreakBase():
    """Base class for mangafreak extractors"""
    category = "mangafreak"
    root = "https://ww2.mangafreak.me"


class MangafreakChapterExtractor(MangafreakBase, ChapterExtractor):
    """Extractor for mangafreak manga chapters"""
    pattern = BASE_PATTERN + r"(/Read1_(.+)_(\d+[a-z]?))"
    example = "https://ww2.mangafreak.me/Read1_Onepunch_Man_1"

    def metadata(self, page):
        extr = text.extract_from(page)
        manga = text.unescape(extr("<title>", " Chapter "))
        title = text.unescape(extr("", " - MangaFreak"))

        chapter_str = self.groups[2]
        chapter, sep, minor = chapter_str.partition("e")

        return {
            "manga"        : manga,
            "title"        : title,
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_string": chapter_str,
            "manga_slug"   : self.groups[1],
            "lang"         : "en",
            "language"     : "English",
        }

    def images(self, page):
        return [
            ("https://images.mangafreak.me/mangas/" + path, None)
            for path in text.extract_iter(
                page, 'src="https://images.mangafreak.me/mangas/', '"')
        ]


class MangafreakMangaExtractor(MangafreakBase, MangaExtractor):
    """Extractor for mangafreak manga series"""
    chapterclass = MangafreakChapterExtractor
    pattern = BASE_PATTERN + r"(/Manga/([^/?#]+))"
    example = "https://ww2.mangafreak.me/Manga/Onepunch_Man"

    def chapters(self, page):
        extr = text.extract_from(page)
        manga = text.unescape(extr("<title>", " Manga"))

        chapter_table = text.extr(page, "<table>", "</table>")
        if not chapter_table:
            return []

        data = {
            "manga"     : manga,
            "manga_slug": self.groups[1],
            "lang"      : "en",
            "language"  : "English",
        }

        results = []
        for row in text.extract_iter(chapter_table, "<tr>", "</tr>"):
            href = text.extr(row, '<a href="', '"')
            if not href:
                continue
            url = self.root + href
            chapter_str = url.rpartition("_")[2]
            chapter, sep, minor = chapter_str.partition("e")

            results.append((url, {
                "chapter"      : text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_string": chapter_str,
                **data,
            }))

        return results
