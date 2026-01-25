# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.mangatown.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangatown\.com"


class MangatownBase():
    """Base class for mangatown extractors"""
    category = "mangatown"
    root = "https://www.mangatown.com"


class MangatownChapterExtractor(MangatownBase, ChapterExtractor):
    """Extractor for manga-chapters from mangatown.com"""
    pattern = BASE_PATTERN + r"(/manga/[^/?#]+(?:/v0*(\d+))?/c(\d+[^/?#]*))"
    example = "https://www.mangatown.com/manga/TITLE/c001/1.html"

    def __init__(self, match):
        self.part, self.volume, self.chapter = match.groups()
        self.base = f"{self.root}{self.part}/"
        ChapterExtractor.__init__(self, match, self.base + "1.html")

    def metadata(self, page):
        manga, pos = text.extract(
            page, 'property="og:title" content="', '"')
        count     , pos = text.extract(page, "total_pages = ", ";", pos)
        manga_id  , pos = text.extract(page, "series_id=", ";", pos)
        chapter_id, pos = text.extract(page, "chapter_id=", ";", pos)

        chapter, dot, minor = self.chapter.partition(".")

        return {
            "manga"   : text.unescape(manga),
            "manga_id": text.parse_int(manga_id),
            "volume"  : text.parse_int(self.volume),
            "chapter" : text.parse_int(chapter),
            "chapter_minor": dot + minor,
            "chapter_id": text.parse_int(chapter_id),
            "count"   : text.parse_int(count),
            "lang"    : "en",
            "language": "English",
        }

    def images(self, page):
        pnum = 1

        while True:
            url = (text.extr(page, 'id="image" src="', '"') or
                   text.extr(page, '<img src="', '"'))
            if not url:
                return
            yield text.ensure_http_scheme(url), None
            pnum += 1
            page = self.request(f"{self.base}{pnum}.html").text


class MangatownMangaExtractor(MangatownBase, MangaExtractor):
    """Extractor for manga from mangatown.com"""
    chapterclass = MangatownChapterExtractor
    pattern = BASE_PATTERN + r"(/manga/[^/?#]+)"
    example = "https://www.mangatown.com/manga/TITLE"

    def chapters(self, page):
        results = []

        manga, pos = text.extract(page, '<title>', '</title>')
        manga = manga.partition(" Manga")[0].replace("Read ", "", 1)
        manga = text.unescape(manga)

        page = text.extract(page, 'class="chapter_list"', '</ul>', pos)[0]
        for ch in text.extract_iter(page, "<li>", "</li>"):
            path , pos = text.extract(ch, '<a href="', '"')
            title, pos = text.extract(ch, "<span>", "<", pos)
            date , pos = text.extract(ch, 'class="time">', "<", pos)

            chapter = text.extr(path, "/c", "/")
            chapter, sep, minor = chapter.partition(".")

            results.append((self.root + path, {
                "manga"   : manga,
                "chapter" : text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "title"   : "" if title is None else text.unescape(title),
                "date"    : date,
                "lang"    : "en",
                "language": "English",
            }))
        return results
