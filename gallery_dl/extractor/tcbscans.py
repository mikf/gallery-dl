# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://onepiecechapters.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text


class TcbscansChapterExtractor(ChapterExtractor):
    category = "tcbscans"
    pattern = (r"(?:https?://)?onepiecechapters\.com"
               r"(/chapters/\d+/[^/?#]+)")
    root = "https://onepiecechapters.com"
    test = (
        (("https://onepiecechapters.com"
          "/chapters/4708/chainsaw-man-chapter-108"), {
            "pattern": (r"https://cdn\.[^/]+"
                        r"/(file|attachments/[^/]+)/[^/]+/[^.]+\.\w+"),
            "count"  : 17,
            "keyword": {
                "manga": "Chainsaw Man",
                "chapter": 108,
                "chapter_minor": "",
                "lang": "en",
                "language": "English",
            },
        }),
        ("https://onepiecechapters.com/chapters/4716/one-piece-chapter-1065", {
            "pattern": (r"https://cdn\.[^/]+"
                        r"/(file|attachments/[^/]+)/[^/]+/[^.]+\.\w+"),
            "count"  : 18,
            "keyword": {
                "manga": "One Piece",
                "chapter": 1065,
                "chapter_minor": "",
                "lang": "en",
                "language": "English",
            },
        }),
        (("https://onepiecechapters.com/"
          "chapters/44/ace-novel-manga-adaptation-chapter-1")),
    )

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(
                page, '<img class="fixed-ratio-content" src="', '"')
        ]

    def metadata(self, page):
        manga, _, chapter = text.extr(
            page, 'font-bold mt-8">', "</h1>").rpartition(" - Chapter ")
        chapter, sep, minor = chapter.partition(".")
        return {
            "manga": text.unescape(manga),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "lang": "en", "language": "English",
        }


class TcbscansMangaExtractor(MangaExtractor):
    category = "tcbscans"
    chapterclass = TcbscansChapterExtractor
    pattern = (r"(?:https?://)?onepiecechapters\.com"
               r"(/mangas/\d+/[^/?#]+)")
    root = "https://onepiecechapters.com"
    test = (
        ("https://onepiecechapters.com/mangas/13/chainsaw-man", {
            "pattern": TcbscansChapterExtractor.pattern,
            "range"  : "1-50",
            "count"  : 50,
        }),
        ("https://onepiecechapters.com/mangas/4/jujutsu-kaisen", {
            "pattern": TcbscansChapterExtractor.pattern,
            "range"  : "1-50",
            "count"  : 50,
        }),
        ("https://onepiecechapters.com/mangas/15/hunter-x-hunter"),
    )

    def chapters(self, page):
        data = {
            "manga": text.unescape(text.extr(
                page, 'class="my-3 font-bold text-3xl">', "</h1>")),
            "lang": "en", "language": "English",
        }

        results = []
        page = text.extr(page, 'class="col-span-2"', 'class="order-1')
        for chapter in text.extract_iter(page, "<a", "</a>"):
            url = text.extr(chapter, 'href="', '"')
            data["title"] = text.unescape(text.extr(
                chapter, 'text-gray-500">', "</div>"))
            chapter = text.extr(
                chapter, 'font-bold">', "</div>").rpartition(" Chapter ")[2]
            chapter, sep, minor = chapter.partition(".")
            data["chapter"] = text.parse_int(chapter)
            data["chapter_minor"] = sep + minor
            results.append((self.root + url, data.copy()))
        return results
