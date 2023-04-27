# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://manganato.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?((?:chap|read|www\.|m\.)?mangan(?:at|el)o\.com)"


class ManganeloBase():
    category = "manganelo"
    root = "https://chapmanganato.com"
    _match_chapter = None

    def __init__(self, match):
        domain, path = match.groups()
        super().__init__(match, "https://" + domain + path)
        self.session.headers['Referer'] = self.root

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
    test = (
        ("https://chapmanganato.com/manga-gn983696/chapter-23", {
            "pattern": r"https://v\d+\.mkklcdnv6tempv5\.com/img/tab_17/03/23"
                       r"/39/gn983696/vol_3_chapter_23_24_yen/\d+-[no]\.jpg",
            "keyword": "17faaea7f0fb8c2675a327bf3aa0bcd7a6311d68",
            "count": 25,
        }),
        ("https://chapmanganelo.com/manga-ti107776/chapter-4", {
            "pattern": r"https://v\d+\.mkklcdnv6tempv5\.com/img/tab_17/01/92"
                       r"/08/ti970565/chapter_4_caster/\d+-o\.jpg",
            "keyword": "06e01fa9b3fc9b5b954c0d4a98f0153b40922ded",
            "count": 45,
        }),
        ("https://chapmanganato.com/manga-no991297/chapter-8", {
            "keyword": {"chapter": 8, "chapter_minor": "-1"},
            "count": 20,
        }),
        ("https://readmanganato.com/manga-gn983696/chapter-23"),
        ("https://manganelo.com/chapter/gamers/chapter_15"),
        ("https://manganelo.com/chapter/gq921227/chapter_23"),
    )

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
            page, 'class="container-chapter-reader', '\n<div')
        return [
            (url, None)
            for url in text.extract_iter(page, '<img src="', '"')
        ] or [
            (url, None)
            for url in text.extract_iter(
                page, '<img class="reader-content" src="', '"')
        ]


class ManganeloMangaExtractor(ManganeloBase, MangaExtractor):
    """Extractor for manga from manganelo.com"""
    chapterclass = ManganeloChapterExtractor
    pattern = BASE_PATTERN + r"(/(?:manga[-/]|read_)\w+)/?$"
    test = (
        ("https://chapmanganato.com/manga-gn983696", {
            "pattern": ManganeloChapterExtractor.pattern,
            "count": ">= 25",
        }),
        ("https://m.manganelo.com/manga-ti107776", {
            "pattern": ManganeloChapterExtractor.pattern,
            "count": ">= 12",
        }),
        ("https://readmanganato.com/manga-gn983696"),
        ("https://manganelo.com/manga/read_otome_no_teikoku"),
        ("https://manganelo.com/manga/ol921234/"),
    )

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
