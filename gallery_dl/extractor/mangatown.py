# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.mangatown.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text


class MangatownBase():
    """Base class for mangatown extractors"""
    category = "mangatown"
    root = "https://www.mangatown.com"


class MangatownChapterExtractor(MangatownBase, ChapterExtractor):
    """Extractor for manga-chapters from mangatown.com"""
    pattern = (r"(?:https?://)?(?:www\.)?mangatown\.com"
               r"(/manga/[^/]+(?:/v0*(\d+))?/c(\d+[^/?#]*))")
    example = "https://www.mangatown.com/manga/TITLE/c001/1.html"

    def __init__(self, match):
        self.part, self.volume, self.chapter = match.groups()
        self.base = f"{self.root}/manga/{self.part}/"
        ChapterExtractor.__init__(self, match, self.base + "1.html")

    def metadata(self, page):
        manga, pos = text.extract(page, '<title>', '</title>')
        manga = manga.partition(" Manga")[0].replace("Read ", "", 1)

        count     , pos = text.extract(page, "total_pages = ", ";", pos)
        manga_id  , pos = text.extract(page, "series_id = ", ";", pos)
        chapter_id, pos = text.extract(page, "chapter_id = ", ";", pos)

        chapter, dot, minor = self.chapter.partition(".")

        return {
            "manga": text.unescape(manga),
            "manga_id": text.parse_int(manga_id),
            "volume": text.parse_int(self.volume),
            "chapter": text.parse_int(chapter),
            "chapter_minor": dot + minor,
            "chapter_id": text.parse_int(chapter_id),
            "count": text.parse_int(count),
            "lang": "en",
            "language": "English",
        }

    def images(self, page):
        pnum = 1

        while True:
            url, pos = text.extract(page, 'id="image" src="', '"')
            if not url:
                url, pos = text.extract(page, '<img src="', '"')
            if not url:
                return
            yield text.ensure_http_scheme(url), None
            pnum += 1
            page = self.request(f"{self.base}{pnum}.html").text


class MangatownMangaExtractor(MangatownBase, MangaExtractor):
    """Extractor for manga from mangatown.com"""
    chapterclass = MangatownChapterExtractor
    pattern = (r"(?:https?://)?(?:www\.)?mangatown\.com"
               r"(/manga/[^/?#]+)/?$")
    example = "https://www.mangatown.com/manga/TITLE"

    def chapters(self, page):
        results = []

        manga, pos = text.extract(page, '<title>', '</title>')
        manga = manga.partition(" Manga")[0].replace("Read ", "", 1)
        manga = text.unescape(manga)

        page = text.extract(
            page, 'class="chapter_list"', '</ul>', pos)[0]

        pos = 0
        while True:
            url, pos = text.extract(page, '<a href="', '"', pos)
            if not url:
                return results
            url = text.urljoin(self.root, url)
            title, pos = text.extract(page, '>', '<', pos)
            date , pos = text.extract(page, 'class="time"', '</span>', pos)
            date = text.remove_html(date).strip()

            results.append((url, {
                "manga": manga,
                "title": text.unescape(title),
                "date": date,
                "lang": "en",
                "language": "English",
            }))
