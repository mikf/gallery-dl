# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rawkuma.net/"""

from .common import MangaExtractor, ChapterExtractor
from .. import text, util
import re

BASE_PATTERN = r"(?:https?://)?rawkuma\.(?:net|com)"


class RawkumaBase():
    """Base class for rawkuma extractors"""
    category = "rawkuma"
    root = "https://rawkuma.net"

    def get_title(self, page):
        title = text.extr(page, 'property="og:title" content="', '"')
        title = text.unescape(title).strip()
        m = re.search(
            r"(.+) (?:Manga|Chapter \d+) (?:Raw - Rawkuma)", title)
        if m:
            title = m.group(1)
        return title


class RawkumaChapterExtractor(RawkumaBase, ChapterExtractor):
    """Extractor for manga chapters from rawkuma.net"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = BASE_PATTERN + r"/([^/?#]+)-chapter-(\d+)"
    example = "https://rawkuma.net/TITLE-chapter-123"

    def __init__(self, match):
        url = match.group(0)
        self.gid, self.chapter = match.groups()
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = self.get_title(page)
        chapter, sep, minor = self.chapter.partition(".")
        return {
            "manga": title,
            "manga_id": self.gid,
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": "%s-chapter-%s" % (self.gid, self.chapter),
        }

    def images(self, page):
        results = []
        pos = 0
        json, pos = text.extract(page, "<script>ts_reader.run(",
                                 ");</script>", pos)
        json_data = util.json_loads(json)
        source = json_data.get("sources", [{}])[0]
        images = source.get("images", [])

        for url in images:
            results.append((url, None))

        return results


class RawkumaMangaExtractor(RawkumaBase, MangaExtractor):
    """Extractor for manga from rawkuma.net"""
    chapterclass = RawkumaChapterExtractor
    pattern = BASE_PATTERN + r"/manga/([^/?#]+)"
    example = "https://rawkuma.net/manga/TITLE/"

    def __init__(self, match):
        url = "{}/manga/{}/".format(self.root, match.group(1))
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
