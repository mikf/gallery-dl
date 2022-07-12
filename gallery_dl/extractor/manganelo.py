# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://manganato.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re

BASE_PATTERN = \
    r"(?:https?://)?((?:(?:read)?manganato|(?:www\.)?manganelo)\.com)"


class ManganeloChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from manganelo.com"""
    category = "manganelo"
    root = "https://readmanganato.com"
    pattern = BASE_PATTERN + r"(/(?:manga-\w+|chapter/\w+)/chapter[-_][^/?#]+)"
    test = (
        ("https://readmanganato.com/manga-gn983696/chapter-23", {
            "pattern": r"https://v\d+\.mkklcdnv6tempv5\.com/img/tab_17/03/23"
                       r"/39/gn983696/vol_3_chapter_23_24_yen/\d+-[no]\.jpg",
            "keyword": "2c5cd59342f149375df9bcb50aa416b4d04a43cf",
            "count": 25,
        }),
        ("https://manganelo.com/chapter/gamers/chapter_15"),
        ("https://manganelo.com/chapter/gq921227/chapter_23"),
    )

    def __init__(self, match):
        domain, path = match.groups()
        ChapterExtractor.__init__(self, match, "https://" + domain + path)
        self.session.headers['Referer'] = self.root

    def metadata(self, page):
        _     , pos = text.extract(page, '<a class="a-h" ', '/a>')
        manga , pos = text.extract(page, '<a class="a-h" ', '/a>', pos)
        info  , pos = text.extract(page, '<a class="a-h" ', '/a>', pos)
        author, pos = text.extract(page, '- Author(s) : ', '</p>', pos)

        manga, _ = text.extract(manga, '">', '<')
        info , _ = text.extract(info , '">', '<')
        match = re.match(
            r"(?:[Vv]ol\. *(\d+) )?"
            r"[Cc]hapter *([^:]*)"
            r"(?:: *(.+))?", info)
        volume, chapter, title = match.groups() if match else ("", "", info)
        chapter, sep, minor = chapter.partition(".")

        return {
            "manga"        : text.unescape(manga),
            "title"        : text.unescape(title) if title else "",
            "author"       : text.unescape(author) if author else "",
            "volume"       : text.parse_int(volume),
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "lang"         : "en",
            "language"     : "English",
        }

    def images(self, page):
        page = text.extract(
            page, 'class="container-chapter-reader', '\n<div')[0]
        return [
            (url, None)
            for url in text.extract_iter(page, '<img src="', '"')
        ]


class ManganeloMangaExtractor(MangaExtractor):
    """Extractor for manga from manganelo.com"""
    category = "manganelo"
    root = "https://readmanganato.com"
    chapterclass = ManganeloChapterExtractor
    pattern = BASE_PATTERN + r"(/(?:manga[-/]|read_)\w+)/?$"
    test = (
        ("https://readmanganato.com/manga-gn983696", {
            "pattern": ManganeloChapterExtractor.pattern,
            "count": ">= 25",
        }),
        ("https://manganelo.com/manga/read_otome_no_teikoku"),
        ("https://manganelo.com/manga/ol921234/"),
    )

    def __init__(self, match):
        domain, path = match.groups()
        MangaExtractor.__init__(self, match, "https://" + domain + path)
        self.session.headers['Referer'] = self.root

    def chapters(self, page):
        results = []
        data = self.parse_page(page, {"lang": "en", "language": "English"})

        needle = 'class="chapter-name text-nowrap" href="'
        pos = page.index('<ul class="row-content-chapter">')
        while True:
            url, pos = text.extract(page, needle, '"', pos)
            if not url:
                return results
            data["title"], pos = text.extract(page, '>', '</a>', pos)
            data["date"] , pos = text.extract(
                page, 'class="chapter-time text-nowrap" title="', '">', pos)
            chapter, sep, minor = url.rpartition("/chapter_")[2].partition(".")
            data["chapter"] = text.parse_int(chapter)
            data["chapter_minor"] = sep + minor
            results.append((url, data.copy()))

    @staticmethod
    def parse_page(page, data):
        """Parse metadata on 'page' and add it to 'data'"""
        text.extract_all(page, (
            ("manga"  , '<h1>', '</h1>'),
            ('author' , '</i>Author(s) :</td>', '</tr>'),
        ), values=data)
        data["author"] = text.remove_html(data["author"])
        return data
