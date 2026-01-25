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

    def __init__(self, match):
        ChapterExtractor.__init__(self, match, self.root + match.group(1))
        self.manga_slug, self.chapter = match.groups()[1:]

    def metadata(self, page):
        extr = text.extract_from(page)
        manga = text.unescape(extr("<title>", " Chapter "))
        title = text.unescape(extr("", " - MangaFreak"))
        chapter_str = extr("# ", " MANGA ONLINE")

        # Parse chapter number and minor suffix (e.g., "167e" -> chapter=167, minor="e")
        chapter, sep, minor = self.chapter.partition("e") if "e" in self.chapter else (self.chapter, "", "")

        return {
            "manga"        : manga,
            "title"        : title,
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_string": self.chapter,
            "manga_slug"   : self.manga_slug,
            "lang"         : "en",
            "language"     : "English",
        }

    def images(self, page):
        # Extract all <img> tags pointing to manga images
        return [
            (url, None)
            for url in text.extract_iter(page, '<img src="https://images.mangafreak.me/mangas/', '"')
        ]


class MangafreakMangaExtractor(MangafreakBase, MangaExtractor):
    """Extractor for mangafreak manga series"""
    chapterclass = MangafreakChapterExtractor
    pattern = BASE_PATTERN + r"(/Manga/([^/?#]+))"
    example = "https://ww2.mangafreak.me/Manga/Onepunch_Man"

    def __init__(self, match):
        MangaExtractor.__init__(self, match, self.root + match.group(1))
        self.manga_slug = match.group(2)

    def chapters(self, page):
        extr = text.extract_from(page)
        manga = text.unescape(extr("<title>", " Manga"))

        # Extract chapter list from table
        chapter_list = text.extr(page, "<tbody>", "</tbody>")
        if not chapter_list:
            return []

        data = {
            "manga"      : manga,
            "manga_slug" : self.manga_slug,
            "lang"       : "en",
            "language"   : "English",
        }

        results = []
        for row in text.extract_iter(chapter_list, "<tr>", "</tr>"):
            # Extract chapter link and date from each row
            chapter_link = text.extr(row, '<a href="', '"')
            if not chapter_link:
                continue

            # Build full URL if relative
            if chapter_link.startswith("/"):
                url = self.root + chapter_link
            else:
                url = self.root + "/" + chapter_link

            # Parse chapter info from URL like /Read1_Onepunch_Man_167e
            chapter_part = url.rsplit("/", 1)[-1]  # Read1_Onepunch_Man_167e
            if chapter_part.startswith("Read1_"):
                parts = chapter_part.split("_")
                if len(parts) >= 3:
                    chapter_str = parts[-1]
                    # Parse chapter number and minor suffix
                    chapter, sep, minor = chapter_str.partition("e") if "e" in chapter_str else (chapter_str, "", "")

                    chapter_data = {
                        "chapter"      : text.parse_int(chapter),
                        "chapter_minor": sep + minor,
                        "chapter_string": chapter_str,
                        **data,
                    }
                    results.append((url, chapter_data))

        return results
