# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rawkuma.net/"""

from .common import MangaExtractor, ChapterExtractor
from .. import text, util

BASE_PATTERN = r"(?:https?://)?rawkuma\.(?:net|com)"


class RawkumaBase():
    """Base class for rawkuma extractors"""
    category = "rawkuma"
    root = "https://rawkuma.net"


class RawkumaChapterExtractor(RawkumaBase, ChapterExtractor):
    """Extractor for manga chapters from rawkuma.net"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = BASE_PATTERN + r"/([^/?#]+-chapter-\d+(?:-\d+)?)"
    example = "https://rawkuma.net/TITLE-chapter-123/"

    def __init__(self, match):
        url = f"{self.root}/{match[1]}/"
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        item = util.json_loads(text.extr(page, ',"item":', "}};"))
        title = text.rextr(
            page, '<h1 class="entry-title', "</h1>").partition(" &#8211; ")[2]
        date = text.extr(page, 'datetime="', '"')
        chapter, sep, minor = item["c"].partition(".")

        return {
            "manga"        : item["s"],
            "manga_id"     : text.parse_int(item["mid"]),
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id"   : text.parse_int(item["cid"]),
            "title"        : text.unescape(title),
            "date"         : text.parse_datetime(
                date, "%Y-%m-%dWIB%H:%M:%S%z"),
            "thumbnail"    : item.get("t"),
            "lang"         : "ja",
            "language"     : "Japanese",
        }

    def images(self, page):
        images = util.json_loads(text.extr(page, '","images":', '}'))
        return [(url, None) for url in images]


class RawkumaMangaExtractor(RawkumaBase, MangaExtractor):
    """Extractor for manga from rawkuma.net"""
    chapterclass = RawkumaChapterExtractor
    pattern = BASE_PATTERN + r"/manga/([^/?#]+)"
    example = "https://rawkuma.net/manga/TITLE/"

    def __init__(self, match):
        url = f"{self.root}/manga/{match[1]}/"
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        manga = text.unescape(text.extr(page, "<title>", " &#8211; "))

        results = []
        for chbox in text.extract_iter(
                page, '<li data-num="', "</a>"):
            info = text.extr(chbox, '', '"')
            chapter, _, title = info.partition(" - ")
            chapter, sep, minor = chapter.partition(".")

            results.append((text.extr(chbox, 'href="', '"'), {
                "manga"        : manga,
                "chapter"      : text.parse_int(chapter),
                "chapter-minor": sep + minor,
                "title"        : title,
            }))
        return results
