# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ww2.mangafreak.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:ww[\dw]\.)?mangafreak\.me"


class MangafreakBase():
    """Base class for mangafreak extractors"""
    category = "mangafreak"
    root = "https://ww2.mangafreak.me"


class MangafreakChapterExtractor(MangafreakBase, ChapterExtractor):
    """Extractor for mangafreak manga chapters"""
    pattern = BASE_PATTERN + r"(/Read1_([^/?#]+)_((\d+)([a-z])?))"
    example = "https://ww2.mangafreak.me/Read1_Onepunch_Man_1"

    def metadata(self, page):
        manga = text.extr(page, "<title>Read ", " Chapter ")
        title = text.extr(page, 'selected="selected">', "<").partition(": ")[2]
        _, manga_slug, chapter_string, chapter, minor = self.groups

        return {
            "manga"        : text.unescape(manga),
            "manga_slug"   : manga_slug,
            "title"        : text.unescape(title) if title else "",
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": "" if minor is None else minor,
            "chapter_string": chapter_string,
            "lang"         : "en",
            "language"     : "English",
        }

    def images(self, page):
        base = "https://images.mangafreak.me/mangas/"
        return [
            (base + path, None)
            for path in text.extract_iter(page, 'src="' + base, '"')
        ]


class MangafreakMangaExtractor(MangafreakBase, MangaExtractor):
    """Extractor for mangafreak manga series"""
    chapterclass = MangafreakChapterExtractor
    pattern = BASE_PATTERN + r"(/Manga/([^/?#]+))"
    example = "https://ww2.mangafreak.me/Manga/Onepunch_Man"

    def chapters(self, page):
        table = text.extr(page, "<table>", "</table>")
        if not table:
            return ()

        data = {
            "manga"     : text.unescape(text.extr(page, "<title>", " Manga")),
            "manga_slug": self.groups[1],
            "lang"      : "en",
            "language"  : "English",
        }

        results = []
        chapter_match = text.re(r"(\d+)(\w*)").match
        for row in text.extract_iter(table, "<tr>", "</tr>"):
            href = text.extr(row, '<a href="', '"')
            if not href:
                continue
            url = self.root + href
            chapter_string = href.rpartition("_")[2]
            chapter, minor = chapter_match(chapter_string).groups()
            title = text.extr(row, '">', '<').partition(" - ")[2]
            results.append((url, {
                "chapter"       : text.parse_int(chapter),
                "chapter_minor" : minor,
                "chapter_string": chapter_string,
                "title"         : text.unescape(title) if title else "",
                **data,
            }))
        return results
