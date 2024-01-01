# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://manganato.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re

BASE_PATTERN = (
    r"(?:https?://)?"
    r"((?:chap|read|www\.|m\.)?mangan(?:at|el)o"
    r"\.(?:to|com))"
)


class ManganeloBase():
    category = "manganelo"
    root = "https://chapmanganato.com"
    _match_chapter = None

    def __init__(self, match):
        domain, path = match.groups()
        super().__init__(match, "https://" + domain + path)

    def _init(self):
        if self._match_chapter is None:
            ManganeloBase._match_chapter = re.compile(
                r"(?:[Vv]ol\.?\s*(\d+)\s?)?"
                r"[Cc]hapter\s*(\d+)([^:]*)"
                r"(?::\s*(.+))?").match

    def _parse_chapter(self, info, manga, author, date=None):
        match = self._match_chapter(info)
        if match:
            volume, chapter, minor, title = match.groups()
        else:
            volume = chapter = minor = ""
            title = info

        return {
            "manga"        : manga,
            "author"       : author,
            "date"         : date,
            "title"        : text.unescape(title) if title else "",
            "volume"       : text.parse_int(volume),
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": minor,
            "lang"         : "en",
            "language"     : "English",
        }


class ManganeloChapterExtractor(ManganeloBase, ChapterExtractor):
    """Extractor for manga chapters from manganelo.com"""
    pattern = BASE_PATTERN + r"(/(?:manga-\w+|chapter/\w+)/chapter[-_][^/?#]+)"
    example = "https://chapmanganato.com/manga-ID/chapter-01"

    def metadata(self, page):
        extr = text.extract_from(page)
        extr('class="a-h"', ">")
        manga = extr('title="', '"')
        info = extr('title="', '"')
        author = extr("- Author(s) : ", "</p>")

        return self._parse_chapter(
            info, text.unescape(manga), text.unescape(author))

    def images(self, page):
        page = text.extr(
            page, 'class="container-chapter-reader', 'class="container')
        return [
            (url, None)
            for url in text.extract_iter(page, '<img src="', '"')
            if not url.endswith("/gohome.png")
        ] or [
            (url, None)
            for url in text.extract_iter(
                page, '<img class="reader-content" src="', '"')
        ]


class ManganeloMangaExtractor(ManganeloBase, MangaExtractor):
    """Extractor for manga from manganelo.com"""
    chapterclass = ManganeloChapterExtractor
    pattern = BASE_PATTERN + r"(/(?:manga[-/]|read_)\w+)/?$"
    example = "https://manganato.com/manga-ID"

    def chapters(self, page):
        results = []
        append = results.append

        extr = text.extract_from(page)
        manga = text.unescape(extr("<h1>", "<"))
        author = text.remove_html(extr("</i>Author(s) :</td>", "</tr>"))

        extr('class="row-content-chapter', '')
        while True:
            url = extr('class="chapter-name text-nowrap" href="', '"')
            if not url:
                return results
            info = extr(">", "<")
            date = extr('class="chapter-time text-nowrap" title="', '"')
            append((url, self._parse_chapter(info, manga, author, date)))
