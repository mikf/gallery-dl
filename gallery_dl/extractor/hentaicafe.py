# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai.cafe/"""

from . import foolslide
from .. import text
from .common import Extractor
from ..cache import memcache
import re


class HentaicafeChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from hentai.cafe"""
    category = "hentaicafe"
    directory_fmt = ("{category}", "{manga}")
    pattern = (r"(?:https?://)?(?:www\.)?hentai\.cafe"
               r"(/manga/read/[^/?&#]+/[a-z-]+/\d+/\d+(?:/\d+)?)")
    test = ("https://hentai.cafe/manga/read/saitom-box/en/0/1/", {
        "url": "8c6a8c56875ba3ed7ab0a74a64f9960077767fc2",
        "keyword": "6913608267d883c82b887303b9ced13821188329",
    })
    root = "https://hentai.cafe"

    def metadata(self, page):
        info = text.unescape(text.extract(page, '<title>', '</title>')[0])
        manga, _, chapter_string = info.partition(" :: ")

        data = self._data(self.gallery_url.split("/")[5])
        data["manga"] = manga
        data["chapter_string"] = chapter_string.rstrip(" :")
        return self.parse_chapter_url(self.gallery_url, data)

    @memcache(keyarg=1)
    def _data(self, manga):
        return {"artist": [], "tags": []}


class HentaicafeMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from hentai.cafe"""
    category = "hentaicafe"
    pattern = (r"(?:https?://)?" + r"(?:www\.)?hentai\.cafe"
               r"(/hc\.fyi/\d+|(?:/manga/series)?/[^/?&#]+)/?$")
    test = (
        # single chapter
        ("https://hentai.cafe/hazuki-yuuto-summer-blues/", {
            "url": "f8e24a07d6fbb7c6a6ec5ad8ad8faf2436f8751b",
            "keyword": "5af1c570bb5f533a32b3375f9cdaa17a0152ba67",
        }),
        # multi-chapter
        ("https://hentai.cafe/saitom-saitom-box/", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
            "keyword": "3c28517d356cac6acbd9895c9eeefae505304078",
        }),
        # new-style URL
        ("https://hentai.cafe/hc.fyi/2782", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
            "keyword": "3c28517d356cac6acbd9895c9eeefae505304078",
        }),
        # foolslide URL
        ("https://hentai.cafe/manga/series/saitom-box/", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
            "keyword": "f0ece32d958f889d8229ed4052716d398a0a875c",
        }),

    )
    root = "https://hentai.cafe"
    reverse = False
    request = Extractor.request
    chapterclass = HentaicafeChapterExtractor

    def chapters(self, page):
        if "/manga/series/" in self.manga_url:
            chapters = foolslide.FoolslideMangaExtractor.chapters(self, page)
            chapters.reverse()
            return chapters

        url   , pos = text.extract(page, '<link rel="canonical" href="', '"')
        tags  , pos = text.extract(page, "<p>Tags: ", "</br>", pos)
        artist, pos = text.extract(page, "\nArtists: ", "</br>", pos)
        manga , pos = text.extract(page, "/manga/read/", "/", pos)
        data = {
            "manga_id": text.parse_int(url.rpartition("/")[2]),
            "tags"    : text.split_html(tags)[::2],
            "artist"  : text.split_html(artist),
        }
        HentaicafeChapterExtractor._data(manga).update(data)

        return [
            (url, data)
            for url in re.findall(
                r'<a +class="x-btn[^"]*" +href="([^"]+)"', page)
        ]
