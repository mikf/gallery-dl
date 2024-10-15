# -*- coding: utf-8 -*-

# Copyright 2020 Jake Mannens
# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangakakalot.tv/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?(?:ww[\dw]?\.)?mangakakalot\.tv"


class MangakakalotBase():
    """Base class for mangakakalot extractors"""
    category = "mangakakalot"
    root = "https://ww8.mangakakalot.tv"


class MangakakalotChapterExtractor(MangakakalotBase, ChapterExtractor):
    """Extractor for manga chapters from mangakakalot.tv"""
    pattern = BASE_PATTERN + r"(/chapter/[^/?#]+/chapter[_-][^/?#]+)"
    example = "https://ww6.mangakakalot.tv/chapter/manga-ID/chapter-01"

    def __init__(self, match):
        self.path = match.group(1)
        ChapterExtractor.__init__(self, match, self.root + self.path)

    def metadata(self, page):
        _     , pos = text.extract(page, '<span itemprop="title">', '<')
        manga , pos = text.extract(page, '<span itemprop="title">', '<', pos)
        info  , pos = text.extract(page, '<span itemprop="title">', '<', pos)
        author, pos = text.extract(page, '. Author:', ' already has ', pos)

        match = re.match(
            r"(?:[Vv]ol\. *(\d+) )?"
            r"[Cc]hapter *([^:]*)"
            r"(?:: *(.+))?", info or "")
        volume, chapter, title = match.groups() if match else ("", "", info)
        chapter, sep, minor = chapter.partition(".")

        return {
            "manga"        : text.unescape(manga),
            "title"        : text.unescape(title) if title else "",
            "author"       : text.unescape(author).strip() if author else "",
            "volume"       : text.parse_int(volume),
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "lang"         : "en",
            "language"     : "English",
        }

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(page, '<img data-src="', '"')
        ]


class MangakakalotMangaExtractor(MangakakalotBase, MangaExtractor):
    """Extractor for manga from mangakakalot.tv"""
    chapterclass = MangakakalotChapterExtractor
    pattern = BASE_PATTERN + r"(/manga/[^/?#]+)"
    example = "https://ww6.mangakakalot.tv/manga/manga-ID"

    def chapters(self, page):
        data = {"lang": "en", "language": "English"}
        data["manga"], pos = text.extract(page, "<h1>", "<")
        author, pos = text.extract(page, "<li>Author(s) :", "</a>", pos)
        data["author"] = text.remove_html(author)

        results = []
        for chapter in text.extract_iter(page, '<div class="row">', '</div>'):
            url, pos = text.extract(chapter, '<a href="', '"')
            title, pos = text.extract(chapter, '>', '</a>', pos)
            data["title"] = title.partition(": ")[2]
            data["date"] , pos = text.extract(
                chapter, '<span title=" ', '"', pos)

            chapter, sep, minor = url.rpartition("/chapter-")[2].partition(".")
            data["chapter"] = text.parse_int(chapter)
            data["chapter_minor"] = sep + minor

            if url[0] == "/":
                url = self.root + url
            results.append((url, data.copy()))
        return results
