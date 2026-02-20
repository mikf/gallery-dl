# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangafire.to/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangafire\.to"


class MangafireBase():
    """Base class for mangafire extractors"""
    category = "mangafire"
    root = "https://mangafire.to"

    def _manga_info(self, manga_path, page=None):
        if page is None:
            url = f"{self.root}/manga/{manga_path}"
            page = self.request(url).text
        slug, _, mid = manga_path.rpartition(".")

        extr = text.extract_from(page)
        manga = {
            "cover": text.extr(extr(
                'class="poster">', '</div>'), 'src="', '"'),
            "status": extr("<p>", "<").replace("_", " ").title(),
            "manga"     : text.unescape(extr(
                'itemprop="name">', "<")),
            "manga_id": mid,
            "manga_slug": slug,
            "manga_titles": text.unescape(extr(
                "<h6>", "<")).split("; "),
            "type": text.remove_html(extr(
                'class="min-info">', "</a>")),
            "author": text.unescape(text.remove_html(extr(
                "<span>Author:</span>", "</div>"))).split(" , "),
            "published": text.remove_html(extr(
                "<span>Published:</span>", "</div>")),
            "tags": text.split_html(extr(
                "<span>Genres:</span>", "</div>"))[::2],
            "publisher": text.unescape(text.remove_html(extr(
                "<span>Mangazines:</span>", "</div>"))).split(" , "),
            "score": text.parse_float(text.remove_html(extr(
                'class="score">', " / "))),
            "description": text.remove_html(extr(
                'id="synopsis">', "<script>")),
        }

        if len(lst := manga["author"]) == 1 and not lst[0]:
            manga["author"] = ()
        if len(lst := manga["publisher"]) == 1 and not lst[0]:
            manga["publisher"] = ()

        return manga

    def _manga_chapters(self, manga_info):
        manga_id, type, lang = manga_info
        url = f"{self.root}/ajax/read/{manga_id}/{type}/{lang}"
        params = {"vrf": self.utils("vrf").generate(
            f"{manga_id}@{type}@{lang}")}
        headers = {"x-requested-with": "XMLHttpRequest"}
        data = self.request_json(url, params=params, headers=headers)

        needle = f"{manga_id}/{lang}/"
        return {
            text.extr(anchor, needle, '"'): anchor
            for anchor in text.extract_iter(data["result"]["html"], "<a ", ">")
        }

    def _chapter_info(self, info):
        _, lang, chapter_info = text.extr(info, 'href="', '"').rsplit("/", 2)

        if chapter_info.startswith("vol"):
            volume = text.extr(info, 'data-number="', '"')
            volume_id = text.parse_int(text.extr(info, 'data-id="', '"'))
            return {
                "volume"        : text.parse_int(volume),
                "volume_id"     : volume_id,
                "chapter"       : 0,
                "chapter_minor" : "",
                "chapter_string": chapter_info,
                "chapter_id"    : volume_id,
                "title"         : text.unescape(text.extr(
                    info, 'title="', '"')),
                "lang"          : lang,
            }

        chapter, sep, minor = text.extr(
            info, 'data-number="', '"').partition(".")
        return {
            "chapter"       : text.parse_int(chapter),
            "chapter_minor" : sep + minor,
            "chapter_string": chapter_info,
            "chapter_id"    : text.parse_int(text.extr(
                info, 'data-id="', '"')),
            "title"         : text.unescape(text.extr(
                info, 'title="', '"')),
            "lang"          : lang,
        }


class MangafireChapterExtractor(MangafireBase, ChapterExtractor):
    """Extractor for mangafire manga chapters"""
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}{chapter:?c//>03}{chapter_minor:?//}{title:?: //}")
    filename_fmt = (
        "{manga}{volume:?_v//>02}{chapter:?_c//>03}{chapter_minor:?//}_"
        "{page:>03}.{extension}")
    archive_fmt = (
        "{manga_id}_{chapter_id}_{page}")
    pattern = (BASE_PATTERN + r"/read/([\w-]+\.(\w+))/([\w-]+)"
               r"/((chapter|volume)-\d+(?:\D.*)?)")
    example = "https://mangafire.to/read/MANGA.ID/LANG/chapter-123"

    def metadata(self, _):
        manga_path, manga_id, lang, chapter_info, self.type = self.groups

        try:
            chapters = self.cache(
                self._manga_chapters, (manga_id, self.type, lang))
            anchor = chapters[chapter_info]
        except KeyError:
            raise self.exc.NotFoundError("chapter")
        self.chapter_id = text.extr(anchor, 'data-id="', '"')

        return {
            **self.cache(self._manga_info, manga_path),
            **self.cache(self._chapter_info, anchor),
        }

    def images(self, page):
        url = f"{self.root}/ajax/read/{self.type}/{self.chapter_id}"
        params = {"vrf": self.utils("vrf").generate(
            f"{self.type}@{self.chapter_id}")}
        headers = {"x-requested-with": "XMLHttpRequest"}
        data = self.request_json(url, params=params, headers=headers)

        return [
            (image[0], None)
            for image in data["result"]["images"]
        ]


class MangafireMangaExtractor(MangafireBase, MangaExtractor):
    """Extractor for mangafire manga"""
    chapterclass = MangafireChapterExtractor
    pattern = BASE_PATTERN + r"/manga/([\w-]+)\.(\w+)"
    example = "https://mangafire.to/manga/MANGA.ID"

    def chapters(self, page):
        manga_slug, manga_id = self.groups
        lang = self.config("lang") or "en"

        manga = self.cache(
            self._manga_info, f"{manga_slug}.{manga_id}")
        chapters = self.cache(
            self._manga_chapters, (manga_id, "chapter", lang))

        return [
            (self.root + text.extr(anchor, 'href="', '"'), {
                **manga,
                **self.cache(self._chapter_info, anchor),
            })
            for anchor in chapters.values()
        ]
