# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai2read.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
import re


class Hentai2readBase():
    """Base class for hentai2read extractors"""
    category = "hentai2read"
    root = "https://hentai2read.com"


class Hentai2readChapterExtractor(Hentai2readBase, ChapterExtractor):
    """Extractor for a single manga chapter from hentai2read.com"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = r"(?:https?://)?(?:www\.)?hentai2read\.com(/[^/?#]+/([^/?#]+))"
    example = "https://hentai2read.com/TITLE/1/"

    def metadata(self, page):
        title, pos = text.extract(page, "<title>", "</title>")
        manga_id, pos = text.extract(page, 'data-mid="', '"', pos)
        chapter_id, pos = text.extract(page, 'data-cid="', '"', pos)
        chapter, sep, minor = self.groups[1].partition(".")

        match = re.match(r"Reading (.+) \(([^)]+)\) Hentai(?: by (.*))? - "
                         r"([^:]+): (.+) . Page 1 ", title)
        if match:
            manga, type, author, _, title = match.groups()
        else:
            self.log.warning("Failed to extract 'manga', 'type', 'author', "
                             "and 'title' metadata")
            manga = type = author = title = ""

        return {
            "manga": manga,
            "manga_id": text.parse_int(manga_id),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": text.parse_int(chapter_id),
            "type": type,
            "author": author,
            "title": title,
            "lang": "en",
            "language": "English",
        }

    def images(self, page):
        images = text.extract(page, "'images' : ", ",\n")[0]
        return [
            ("https://hentaicdn.com/hentai" + part, None)
            for part in util.json_loads(images)
        ]


class Hentai2readMangaExtractor(Hentai2readBase, MangaExtractor):
    """Extractor for hmanga from hentai2read.com"""
    chapterclass = Hentai2readChapterExtractor
    pattern = r"(?:https?://)?(?:www\.)?hentai2read\.com(/[^/?#]+)/?$"
    example = "https://hentai2read.com/TITLE/"

    def chapters(self, page):
        results = []

        pos = page.find('itemscope itemtype="http://schema.org/Book') + 1
        manga, pos = text.extract(
            page, '<span itemprop="name">', '</span>', pos)
        mtype, pos = text.extract(
            page, '<small class="text-danger">[', ']</small>', pos)
        manga_id = text.parse_int(text.extract(
            page, 'data-mid="', '"', pos)[0])

        while True:
            chapter_id, pos = text.extract(page, ' data-cid="', '"', pos)
            if not chapter_id:
                return results
            _  , pos = text.extract(page, ' href="', '"', pos)
            url, pos = text.extract(page, ' href="', '"', pos)

            chapter, pos = text.extract(page, '>', '<', pos)
            chapter, _, title = text.unescape(chapter).strip().partition(" - ")
            chapter, sep, minor = chapter.partition(".")

            results.append((url, {
                "manga": manga,
                "manga_id": manga_id,
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": text.parse_int(chapter_id),
                "type": mtype,
                "title": title,
                "lang": "en",
                "language": "English",
            }))
