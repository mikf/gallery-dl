# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fanfox.net/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.|m\.)?(?:fanfox\.net|mangafox\.me)"


class MangafoxChapterExtractor(ChapterExtractor):
    """Extractor for manga chapters from fanfox.net"""
    category = "mangafox"
    root = "https://m.fanfox.net"
    pattern = BASE_PATTERN + \
        r"(/manga/[^/?#]+/((?:v([^/?#]+)/)?c(\d+)([^/?#]*)))"
    example = "https://fanfox.net/manga/TITLE/v01/c001/1.html"

    def __init__(self, match):
        base, self.cstr, self.volume, self.chapter, self.minor = match.groups()
        self.urlbase = self.root + base
        ChapterExtractor.__init__(self, match, self.urlbase + "/1.html")

    def metadata(self, page):
        manga, pos = text.extract(page, "<title>", "</title>")
        count, pos = text.extract(
            page, ">", "<", page.find("</select>", pos) - 40)
        sid  , pos = text.extract(page, "var series_id =", ";", pos)
        cid  , pos = text.extract(page, "var chapter_id =", ";", pos)

        return {
            "manga"         : text.unescape(manga),
            "volume"        : text.parse_int(self.volume),
            "chapter"       : text.parse_int(self.chapter),
            "chapter_minor" : self.minor or "",
            "chapter_string": self.cstr,
            "count"         : text.parse_int(count),
            "sid"           : text.parse_int(sid),
            "cid"           : text.parse_int(cid),
        }

    def images(self, page):
        pnum = 1
        while True:
            url, pos = text.extract(page, '<img src="', '"')
            yield text.ensure_http_scheme(text.unescape(url)), None
            url, pos = text.extract(page, ' src="', '"', pos)
            yield text.ensure_http_scheme(text.unescape(url)), None

            pnum += 2
            page = self.request("{}/{}.html".format(self.urlbase, pnum)).text


class MangafoxMangaExtractor(MangaExtractor):
    """Extractor for manga from fanfox.net"""
    category = "mangafox"
    root = "https://m.fanfox.net"
    chapterclass = MangafoxChapterExtractor
    pattern = BASE_PATTERN + r"(/manga/[^/?#]+)/?$"
    example = "https://fanfox.net/manga/TITLE"

    def chapters(self, page):
        results = []
        chapter_match = MangafoxChapterExtractor.pattern.match

        extr = text.extract_from(page)
        manga = extr('<p class="title">', '</p>')
        author = extr('<p>Author(s):', '</p>')
        extr('<dd class="chlist">', '')

        genres, _, summary = text.extr(
            page, '<div class="manga-genres">', '</section>'
        ).partition('<div class="manga-summary">')

        data = {
            "manga"      : text.unescape(manga),
            "author"     : text.remove_html(author),
            "description": text.unescape(text.remove_html(summary)),
            "tags"       : text.split_html(genres),
            "lang"       : "en",
            "language"   : "English",
        }

        while True:
            url = "https://" + extr('<a href="//', '"')
            match = chapter_match(url)
            if not match:
                return results
            _, cstr, volume, chapter, minor = match.groups()

            chapter = {
                "volume"        : text.parse_int(volume),
                "chapter"       : text.parse_int(chapter),
                "chapter_minor" : minor or "",
                "chapter_string": cstr,
                "date"          : text.parse_datetime(
                    extr('right">', '</span>'), "%b %d, %Y"),
            }
            chapter.update(data)
            results.append((url, chapter))
