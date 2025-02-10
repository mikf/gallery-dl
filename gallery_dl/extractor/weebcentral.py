# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://weebcentral.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?weebcentral\.com"


class WeebcentralBase():
    category = "weebcentral"
    root = "https://weebcentral.com"
    request_interval = (0.5, 1.5)

    @memcache(keyarg=1)
    def _extract_manga_data(self, manga_id):
        url = "{}/series/{}".format(self.root, manga_id)
        page = self.request(url).text
        extr = text.extract_from(page)

        return {
            "manga_id": manga_id,
            "lang"    : "en",
            "language": "English",
            "manga"   : text.unescape(extr("<title>", " | Weeb Central")),
            "author"  : text.split_html(extr("<strong>Author", "</li>"))[1::2],
            "tags"    : text.split_html(extr("<strong>Tag", "</li>"))[1::2],
            "type"    : text.remove_html(extr("<strong>Type: ", "</li>")),
            "status"  : text.remove_html(extr("<strong>Status: ", "</li>")),
            "release" : text.remove_html(extr("<strong>Released: ", "</li>")),
            "official": ">Yes" in extr("<strong>Official Translatio", "</li>"),
            "description": text.unescape(text.remove_html(extr(
                "<strong>Description", "</li>"))),
        }


class WeebcentralChapterExtractor(WeebcentralBase, ChapterExtractor):
    """Extractor for manga chapters from weebcentral.com"""
    pattern = BASE_PATTERN + r"(/chapters/(\w+))"
    example = "https://weebcentral.com/chapters/01JHABCDEFGHIJKLMNOPQRSTUV"

    def metadata(self, page):
        extr = text.extract_from(page)
        manga_id = extr("'series_id': '", "'")
        chapter_type = extr("'chapter_type': '", "'")
        chapter, sep, minor = extr("'number': '", "'").partition(".")

        data = {
            "chapter": text.parse_int(chapter),
            "chapter_id": self.groups[1],
            "chapter_type": chapter_type,
            "chapter_minor": sep + minor,
        }
        data.update(self._extract_manga_data(manga_id))

        return data

    def images(self, page):
        referer = self.gallery_url
        url = referer + "/images"
        params = {
            "is_prev"      : "False",
            "current_page" : "1",
            "reading_style": "long_strip",
        }
        headers = {
            "Accept"        : "*/*",
            "Referer"       : referer,
            "HX-Request"    : "true",
            "HX-Current-URL": referer,
        }
        page = self.request(url, params=params, headers=headers).text
        extr = text.extract_from(page)

        results = []
        while True:
            src = extr('src="', '"')
            if not src:
                break
            results.append((src, {
                "width" : text.parse_int(extr('width="' , '"')),
                "height": text.parse_int(extr('height="', '"')),
            }))
        return results


class WeebcentralMangaExtractor(WeebcentralBase, MangaExtractor):
    """Extractor for manga from weebcentral.com"""
    chapterclass = WeebcentralChapterExtractor
    pattern = BASE_PATTERN + r"/series/(\w+)"
    example = "https://weebcentral.com/series/01J7ABCDEFGHIJKLMNOPQRSTUV/TITLE"

    def __init__(self, match):
        MangaExtractor.__init__(self, match, False)

    def chapters(self, _):
        manga_id = self.groups[0]
        referer = "{}/series/{}".format(self.root, manga_id)
        url = referer + "/full-chapter-list"
        headers = {
            "Accept"        : "*/*",
            "Referer"       : referer,
            "HX-Request"    : "true",
            "HX-Target"     : "chapter-list",
            "HX-Current-URL": referer,
        }
        page = self.request(url, headers=headers).text
        extr = text.extract_from(page)
        data = self._extract_manga_data(manga_id)
        base = self.root + "/chapters/"

        results = []
        while True:
            chapter_id = extr("/chapters/", '"')
            if not chapter_id:
                break
            type, _, chapter = extr('<span class="">', "<").partition(" ")
            chapter, sep, minor = chapter.partition(".")

            chapter = {
                "chapter_id"   : chapter_id,
                "chapter"      : text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_type" : type,
                "date"         : text.parse_datetime(
                    extr(' datetime="', '"')[:-5], "%Y-%m-%dT%H:%M:%S"),
            }
            chapter.update(data)
            results.append((base + chapter_id, chapter))
        return results
