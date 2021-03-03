# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai.cafe/"""

from . import foolslide
from .. import text
from .common import Extractor, Message
from ..cache import memcache
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?hentai\.cafe"


class HentaicafeBase():
    """Base class for hentaicafe extractors"""
    category = "hentaicafe"
    root = "https://hentai.cafe"

    def _pagination(self, urlfmt):
        data = {"_extractor": HentaicafeMangaExtractor}
        pnum = text.parse_int(self.page_start, 1)

        while True:
            page = self.request(urlfmt(pnum)).text

            for entry in text.extract_iter(
                    page, 'class="entry-featured', 'title="'):
                url = text.extract(entry, 'href="', '"')[0]
                if url:
                    yield Message.Queue, url, data

            if '>&#x2192;<' not in page:
                return
            pnum += 1


class HentaicafeChapterExtractor(HentaicafeBase,
                                 foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from hentai.cafe"""
    directory_fmt = ("{category}", "{manga}")
    filename_fmt = "c{chapter:>03}{chapter_minor:?//}_{page:>03}.{extension}"
    pattern = BASE_PATTERN + r"(/manga/read/[^/?#]+/[a-z-]+/\d+/\d+(?:/\d+)?)"
    test = ("https://hentai.cafe/manga/read/saitom-box/en/0/1/", {
        "url": "8c6a8c56875ba3ed7ab0a74a64f9960077767fc2",
        "keyword": "6913608267d883c82b887303b9ced13821188329",
    })

    def metadata(self, page):
        info = text.unescape(text.extract(page, '<title>', '</title>')[0])
        manga, _, chapter_string = info.partition(" :: ")

        data = self._data(self.gallery_url.split("/")[5])
        if "manga" not in data:
            data["manga"] = manga
        data["chapter_string"] = chapter_string.rstrip(" :")
        return self.parse_chapter_url(self.gallery_url, data)

    @memcache(keyarg=1)
    def _data(self, manga):
        return {"artist": (), "tags": ()}


class HentaicafeMangaExtractor(HentaicafeBase,
                               foolslide.FoolslideMangaExtractor):
    """Extractor for manga from hentai.cafe"""
    pattern = BASE_PATTERN + r"(/hc\.fyi/\d+|(?:/manga/series)?/[^/?#]+)/?$"
    test = (
        # single chapter
        ("https://hentai.cafe/hazuki-yuuto-summer-blues/", {
            "url": "f8e24a07d6fbb7c6a6ec5ad8ad8faf2436f8751b",
            "keyword": "ced644ff94ea22e1991a5e44bf37c38a7e2ac2b3",
        }),
        # multi-chapter
        ("https://hentai.cafe/saitom-saitom-box/", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
            "keyword": "4c2262d680286a54357c334c1faca8f1b0e692e9",
        }),
        # new-style URL
        ("https://hentai.cafe/hc.fyi/2782", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
            "keyword": "4c2262d680286a54357c334c1faca8f1b0e692e9",
        }),
        # foolslide URL
        ("https://hentai.cafe/manga/series/saitom-box/", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
            "keyword": "f0ece32d958f889d8229ed4052716d398a0a875c",
        }),

    )

    def items(self):
        page = Extractor.request(self, self.gallery_url).text

        chapters = self.chapters(page)
        if self.config("chapter-reverse", False):
            chapters.reverse()

        for chapter, data in chapters:
            data["_extractor"] = HentaicafeChapterExtractor
            yield Message.Queue, chapter, data

    def chapters(self, page):
        if "/manga/series/" in self.gallery_url:
            chapters = foolslide.FoolslideMangaExtractor.chapters(self, page)
            chapters.reverse()
            return chapters

        manga , pos = text.extract(page, '<title>', '<')
        url   , pos = text.extract(page, 'rel="canonical" href="', '"', pos)
        tags  , pos = text.extract(page, "<p>Tags: ", "</br>", pos)
        artist, pos = text.extract(page, "\nArtists: ", "</br>", pos)
        key   , pos = text.extract(page, "/manga/read/", "/", pos)
        data = {
            "manga"   : text.unescape(manga.rpartition(" | ")[0]),
            "manga_id": text.parse_int(url.rpartition("/")[2]),
            "tags"    : text.split_html(tags)[::2],
            "artist"  : text.split_html(artist),
        }
        HentaicafeChapterExtractor._data(key).update(data)

        return [
            (url, data)
            for url in re.findall(
                r'<a +class="x-btn[^"]*" +href="([^"]+)"', page)
        ]


class HentaicafeSearchExtractor(HentaicafeBase, Extractor):
    """Extractor for hentaicafe search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(?:page/(\d+)/?)?\?s=([^&#]+)"
    test = ("https://hentai.cafe/?s=benimura", {
        "pattern": HentaicafeMangaExtractor.pattern,
        "count": ">= 10",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page_start, self.search = match.groups()

    def items(self):
        fmt = "{}/page/{}?s={}".format
        return self._pagination(lambda pnum: fmt(self.root, pnum, self.search))


class HentaicafeTagExtractor(HentaicafeBase, Extractor):
    """Extractor for hentaicafe tag/artist searches"""
    subcategory = "tag"
    pattern = (BASE_PATTERN +
               r"/hc\.fyi/(tag|artist|category)/([^/?#]+)(?:/page/(\d+))?")
    test = (
        ("https://hentai.cafe/hc.fyi/tag/vanilla"),
        ("https://hentai.cafe/hc.fyi/category/book/page/5"),
        ("https://hentai.cafe/hc.fyi/artist/benimura-karu", {
            "pattern": HentaicafeMangaExtractor.pattern,
            "count": ">= 10",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.type, self.search, self.page_start = match.groups()

    def items(self):
        fmt = "{}/hc.fyi/{}/{}/page/{}".format
        return self._pagination(
            lambda pnum: fmt(self.root, self.type, self.search, pnum))
