# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rawkuma.net/"""

from .common import MangaExtractor, ChapterExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?rawkuma\.(?:net|com)"


class RawkumaBase():
    """Base class for rawkuma extractors"""
    category = "rawkuma"
    root = "https://rawkuma.net"


class RawkumaChapterExtractor(RawkumaBase, ChapterExtractor):
    """Extractor for manga chapters from rawkuma.net"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = rf"{BASE_PATTERN}(/manga/[^/?#]+/chapter-\d+(?:.\d+)?\.(\d+))"
    example = "https://rawkuma.net/manga/7TITLE/chapter-123.321"

    def __init__(self, match):
        url = f"{self.root}/{match[1]}/"
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        manga, _, chapter = text.extr(
            page, '<title>', "<").rpartition(" Chapter ")
        chapter, sep, minor = chapter.partition(" &#8211; ")[0].partition(".")

        return {
            "manga"        : text.unescape(manga),
            "manga_id"     : text.parse_int(text.extr(page, "manga_id=", "&")),
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id"   : text.parse_int(self.groups[-1]),
            #  "title"        : text.unescape(title),
            "date"         : self.parse_datetime_iso(text.extr(
                page, 'datetime="', '"')),
            "lang"         : "ja",
            "language"     : "Japanese",
        }

    def images(self, page):
        return [(url, None) for url in text.extract_iter(
                page, "<img src='", "'")]


class RawkumaMangaExtractor(RawkumaBase, MangaExtractor):
    """Extractor for manga from rawkuma.net"""
    chapterclass = RawkumaChapterExtractor
    pattern = rf"{BASE_PATTERN}/manga/([^/?#]+)"
    example = "https://rawkuma.net/manga/TITLE/"

    def __init__(self, match):
        url = f"{self.root}/manga/{match[1]}/"
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        manga = text.unescape(text.extr(page, "<title>", " &#8211; "))
        manga_id = text.parse_int(text.extr(page, "manga_id=", "&"))

        url = f"{self.root}/wp-admin/admin-ajax.php"
        params = {
            "manga_id": manga_id,
            "page"    : "1",
            "action"  : "chapter_list",
        }
        headers = {
            "HX-Request"    : "true",
            "HX-Trigger"    : "chapter-list",
            "HX-Target"     : "chapter-list",
            "HX-Current-URL": self.page_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        html = self.request(url, params=params, headers=headers).text

        results = []
        for url in text.extract_iter(html, '<a href="', '"'):
            info = url[url.rfind("-")+1:-1]
            chapter, _, chapter_id = info.rpartition(".")
            chapter, sep, minor = chapter.partition(".")

            results.append((url, {
                "manga"        : manga,
                "manga_id"     : manga_id,
                "chapter"      : text.parse_int(chapter),
                "chapter-minor": sep + minor,
                "chapter_id"   : text.parse_int(chapter_id),
            }))
        return results
