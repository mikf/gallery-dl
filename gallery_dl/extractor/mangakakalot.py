# -*- coding: utf-8 -*-

# Copyright 2020 Jake Mannens
# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangakakalot.tv/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re


class MangakakalotBase():
    """Base class for mangakakalot extractors"""
    category = "mangakakalot"
    root = "https://ww.mangakakalot.tv"


class MangakakalotChapterExtractor(MangakakalotBase, ChapterExtractor):
    """Extractor for manga chapters from mangakakalot.tv"""
    pattern = (r"(?:https?://)?(?:www?\.)?mangakakalot\.tv"
               r"(/chapter/[^/?#]+/chapter[_-][^/?#]+)")
    test = (
        ("https://ww.mangakakalot.tv/chapter/manga-hl984546/chapter-6", {
            "pattern": r"https://cm\.blazefast\.co"
                       r"/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.jpg",
            "keyword": "e9646a76a210f1eb4a71b4134664814c99d65d48",
            "count": 14,
        }),
        (("https://mangakakalot.tv/chapter"
          "/hatarakanai_futari_the_jobless_siblings/chapter_20.1"), {
            "keyword": "14c430737ff600b26a3811815905f34dd6a6c8c6",
            "content": "b3eb1f139caef98d9dcd8ba6a5ee146a13deebc4",
            "count": 2,
        }),
    )

    def __init__(self, match):
        self.path = match.group(1)
        ChapterExtractor.__init__(self, match, self.root + self.path)
        self.session.headers['Referer'] = self.root

    def metadata(self, page):
        _     , pos = text.extract(page, '<span itemprop="title">', '<')
        manga , pos = text.extract(page, '<span itemprop="title">', '<', pos)
        info  , pos = text.extract(page, '<span itemprop="title">', '<', pos)
        author, pos = text.extract(page, '. Author:', ' already has ', pos)

        match = re.match(
            r"(?:[Vv]ol\. *(\d+) )?"
            r"[Cc]hapter *([^:]*)"
            r"(?:: *(.+))?", info)
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
    pattern = (r"(?:https?://)?(?:www?\.)?mangakakalot\.tv"
               r"(/manga/[^/?#]+)")
    test = (
        ("https://ww.mangakakalot.tv/manga/lk921810", {
            "url": "654d040c17728c9c8756fce7092b084e8dcf67d2",
        }),
        ("https://mangakakalot.tv/manga/manga-jk986845", {
            "pattern": MangakakalotChapterExtractor.pattern,
            "count": ">= 30",
        }),
    )

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

            if url.startswith("/"):
                url = self.root + url
            results.append((url, data.copy()))
        return results
