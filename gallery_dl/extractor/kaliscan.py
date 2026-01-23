# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kaliscan.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?kaliscan\.me"


class KaliscanBase():
    """Base class for kaliscan extractors"""
    category = "kaliscan"
    root = "https://kaliscan.me"

    @memcache(keyarg=1)
    def manga_data(self, manga_slug, page=None):
        if not page:
            url = "{}/manga/{}".format(self.root, manga_slug)
            page = self.request(url).text
        extr = text.extract_from(page)

        title = text.unescape(extr("<h1>", "<"))
        alt_titles = extr("<h2>", "<")
        alt_titles = (
            [t.strip() for t in alt_titles.split(",")]
            if alt_titles else []
        )

        author = text.remove_html(extr(
            "Authors :</strong>", "</p>"))
        status = text.remove_html(extr(
            "Status :</strong>", "</p>"))
        genres = [g.strip(" ,") for g in text.split_html(extr(
            "Genres :</strong>", "</p>"))]

        desc_html = extr('class="content"', '<div class="readmore"')
        description = (
            text.remove_html(desc_html.partition(">")[2]).strip()
            if desc_html else ""
        )

        manga_id = text.parse_int(text.extr(page, "bookId =", ";"))

        return {
            "manga"       : title,
            "manga_id"    : manga_id,
            "manga_slug"  : manga_slug,
            "manga_titles": alt_titles,
            "author"      : author,
            "status"      : status,
            "genres"      : genres,
            "description" : description,
            "lang"        : "en",
            "language"    : "English",
        }


class KaliscanChapterExtractor(KaliscanBase, ChapterExtractor):
    """Extractor for kaliscan manga chapters"""
    pattern = BASE_PATTERN + r"(/manga/([\w-]+)/chapter-([\d.]+))"
    example = "https://kaliscan.me/manga/ID-MANGA/chapter-1"

    def __init__(self, match):
        ChapterExtractor.__init__(self, match)
        self.manga_slug = self.groups[1]

    def metadata(self, page):
        extr = text.extract_from(page)

        manga_id = text.parse_int(extr("bookId =", ";"))
        extr("bookSlug =", ";")
        chapter_id = text.parse_int(extr("chapterId =", ";"))
        extr("chapterSlug =", ";")
        chapter_number = extr("chapterNumber =", ";").strip(' "\'')

        chapter, sep, minor = chapter_number.partition(".")

        data = {
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id"   : chapter_id,
        }
        data.update(self.manga_data(self.manga_slug))
        if manga_id:
            data["manga_id"] = manga_id
        return data

    def images(self, page):
        images_str = text.extr(page, 'var chapImages = "', '"')
        if not images_str:
            return []
        return [
            (url, None)
            for url in (u.strip() for u in images_str.split(","))
            if url
        ]


class KaliscanMangaExtractor(KaliscanBase, MangaExtractor):
    """Extractor for kaliscan manga"""
    chapterclass = KaliscanChapterExtractor
    pattern = BASE_PATTERN + r"(/manga/([\w-]+))/?$"
    example = "https://kaliscan.me/manga/ID-MANGA"

    def __init__(self, match):
        MangaExtractor.__init__(self, match)
        self.manga_slug = self.groups[1]

    def chapters(self, page):
        data = self.manga_data(self.manga_slug, page)

        chapter_list = text.extr(page, 'id="chapter-list">', '</ul>')
        if not chapter_list:
            return []

        results = []
        for li in text.extract_iter(chapter_list, "<li", "</li>"):
            url = text.extr(li, 'href="', '"')
            if not url:
                continue
            if url[0] == "/":
                url = self.root + url

            chapter, sep, minor = url.rpartition(
                "/chapter-")[2].partition(".")

            results.append((url, {
                "chapter"      : text.parse_int(chapter),
                "chapter_minor": sep + minor,
                **data,
            }))
        return results
