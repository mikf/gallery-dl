# -*- coding: utf-8 -*-

# Copyright 2017-2022 Mike Fährmann
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
    test = (
        ("http://fanfox.net/manga/kidou_keisatsu_patlabor/v05/c006.2/1.html", {
            "keyword": "5661dab258d42d09d98f194f7172fb9851a49766",
            "content": "5c50c252dcf12ffecf68801f4db8a2167265f66c",
        }),
        ("http://mangafox.me/manga/kidou_keisatsu_patlabor/v05/c006.2/"),
        ("http://fanfox.net/manga/black_clover/vTBD/c295/1.html"),
    )

    def __init__(self, match):
        base, self.cstr, self.volume, self.chapter, self.minor = match.groups()
        self.urlbase = self.root + base
        ChapterExtractor.__init__(self, match, self.urlbase + "/1.html")
        self.session.headers["Referer"] = self.root + "/"

    def metadata(self, page):
        manga, pos = text.extract(page, "<title>", "</title>")
        count, pos = text.extract(
            page, ">", "<", page.find("</select>", pos) - 20)
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
            yield text.ensure_http_scheme(url), None
            url, pos = text.extract(page, ' src="', '"', pos)
            yield text.ensure_http_scheme(url), None

            pnum += 2
            page = self.request("{}/{}.html".format(self.urlbase, pnum)).text


class MangafoxMangaExtractor(MangaExtractor):
    """Extractor for manga from fanfox.net"""
    category = "mangafox"
    root = "https://m.fanfox.net"
    chapterclass = MangafoxChapterExtractor
    pattern = BASE_PATTERN + r"(/manga/[^/?#]+)/?$"
    test = (
        ("https://fanfox.net/manga/kanojo_mo_kanojo", {
            "pattern": MangafoxChapterExtractor.pattern,
            "count": ">=60",
            "keyword": {
                "author": "HIROYUKI",
                "chapter": int,
                "chapter_minor": r"re:^(\.\d+)?$",
                "chapter_string": r"re:(v\d+/)?c\d+",
                "date": "type:datetime",
                "description": "High school boy Naoya gets a confession from M"
                               "omi, a cute and friendly girl. However, Naoya "
                               "already has a girlfriend, Seki... but Momi is "
                               "too good a catch to let go. Momi and Nagoya's "
                               "goal becomes clear: convince Seki to accept be"
                               "ing an item with the two of them. Will she bud"
                               "ge?",
                "lang": "en",
                "language": "English",
                "manga": "Kanojo mo Kanojo",
                "tags": ["Comedy", "Romance", "School Life", "Shounen"],
                "volume": int,
            },
        }),
        ("https://mangafox.me/manga/shangri_la_frontier", {
            "pattern": MangafoxChapterExtractor.pattern,
            "count": ">=45",
        }),
        ("https://m.fanfox.net/manga/sentai_daishikkaku"),
    )

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
