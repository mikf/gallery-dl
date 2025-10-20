# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangataro.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?mangataro\.org"


class MangataroBase():
    """Base class for mangataro extractors"""
    category = "mangataro"
    root = "https://mangataro.org"


class MangataroChapterExtractor(MangataroBase, ChapterExtractor):
    """Extractor for mangataro manga chapters"""
    pattern = rf"{BASE_PATTERN}(/read/([^/?#]+)/(?:[^/?#]*-)?(\d+))"
    example = "https://mangataro.org/read/MANGA/ch123-12345"

    def metadata(self, page):
        _, slug, chapter_id = self.groups
        comic = self._extract_jsonld(page)["@graph"][0]
        chapter = comic["position"]
        minor = chapter - int(chapter)
        desc = comic["description"].split(" - ", 3)

        return {
            **_manga_info(self, slug),
            "title"    : desc[1] if len(desc) > 3 else "",
            "chapter"  : int(chapter),
            "chapter_minor": str(round(minor, 5))[1:] if minor else "",
            "chapter_id"   : text.parse_int(chapter_id),
            "chapter_url"  : comic["url"],
            "date"         : self.parse_datetime_iso(comic["datePublished"]),
            "date_updated" : self.parse_datetime_iso(comic["dateModified"]),
        }

    def images(self, page):
        pos = page.find('class="comic-image-container')
        img, pos = text.extract(page, ' src="', '"', pos)

        images = [(img, None)]
        images.extend(
            (url, None)
            for url in text.extract_iter(page, 'data-src="', '"', pos)
        )
        return images


class MangataroMangaExtractor(MangataroBase, MangaExtractor):
    """Extractor for mangataro manga"""
    chapterclass = MangataroChapterExtractor
    pattern = rf"{BASE_PATTERN}(/manga/([^/?#]+))"
    example = "https://mangataro.org/manga/MANGA"

    def chapters(self, page):
        slug = self.groups[1]
        manga = _manga_info(self, slug)

        results = []
        for url in text.extract_iter(text.extr(
                page, '<div class="chapter-list', '<div id="tab-gallery"'),
                '<a href="', '"'):
            chapter, _, chapter_id = url[url.rfind("/")+3:].rpartition("-")
            chapter, sep, minor = chapter.partition("-")
            results.append((url, {
                **manga,
                "chapter"      : text.parse_int(chapter),
                "chapter_minor": f".{minor}" if sep else "",
                "chapter_id"   : text.parse_int(chapter_id),
            }))
        return results


@memcache(keyarg=1)
def _manga_info(self, slug):
    url = f"{self.root}/manga/{slug}"
    page = self.request(url).text
    manga = self._extract_jsonld(page)

    return {
        "manga"      : manga["name"].rpartition(" | ")[0].rpartition(" ")[0],
        "manga_url"  : manga["url"],
        "cover"      : manga["image"],
        "author"     : manga["author"]["name"].split(", "),
        "genre"      : manga["genre"],
        "status"     : manga["status"],
        "description": text.unescape(text.extr(
            page, 'id="description-content-tab">', "</div></div>")),
        "tags"       : text.split_html(text.extr(
            page, ">Genres</h4>", "</div>")),
        "publisher"  : text.remove_html(text.extr(
            page, '>Serialization</h4>', "</div>")),
    }
