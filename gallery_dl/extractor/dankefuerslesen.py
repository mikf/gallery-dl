# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://danke.moe/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?danke\.moe"


class DankefuerslesenBase():
    """Base class for dankefuerslesen extractors"""
    category = "dankefuerslesen"
    root = "https://danke.moe"

    @memcache(keyarg=1)
    def _manga_info(self, slug):
        url = f"{self.root}/api/series/{slug}/"
        return self.request_json(url)


class DankefuerslesenChapterExtractor(DankefuerslesenBase, ChapterExtractor):
    """Extractor for Danke fürs Lesen manga chapters"""
    pattern = rf"{BASE_PATTERN}/read/manga/([\w-]+)/([\w-]+)"
    example = "https://danke.moe/read/manga/TITLE/123/1/"

    def _init(self):
        self.zip = self.config("zip", False)
        if self.zip:
            self.filename_fmt = f"{self.directory_fmt[-1]}.{{extension}}"
            self.directory_fmt = self.directory_fmt[:-1]

    def metadata(self, page):
        slug, ch = self.groups
        manga = self._manga_info(slug)

        if "-" in ch:
            chapter, sep, minor = ch.rpartition("-")
            ch = ch.replace("-", ".")
            minor = "." + minor
        else:
            chapter = ch
            minor = ""

        data = manga["chapters"][ch]
        group_id, self._files = next(iter(data["groups"].items()))

        if not self.zip:
            self.base = (f"{self.root}/media/manga/{slug}/chapters"
                         f"/{data['folder']}/{group_id}/")

        return {
            "manga"     : manga["title"],
            "manga_slug": manga["slug"],
            "author"    : manga["author"],
            "artist"    : manga["artist"],
            "description": manga["description"],
            "title"     : data["title"],
            "volume"    : text.parse_int(data["volume"]),
            "chapter"   : text.parse_int(chapter),
            "chapter_minor": minor,
            "group"     : manga["groups"][group_id].split(" & "),
            "group_id"  : text.parse_int(group_id),
            "date"      : self.parse_timestamp(data["release_date"][group_id]),
            "lang"      : util.NONE,
            "language"  : util.NONE,
        }

    def images(self, page):
        if self.zip:
            return ()

        base = self.base
        return [(base + file, None) for file in self._files]

    def assets(self, page):
        if self.zip:
            slug, ch = self.groups
            url = f"{self.root}/api/download_chapter/{slug}/{ch}/"
            return ({
                "type"     : "archive",
                "extension": "zip",
                "url"      : url,
            },)


class DankefuerslesenMangaExtractor(DankefuerslesenBase, MangaExtractor):
    """Extractor for Danke fürs Lesen manga"""
    chapterclass = DankefuerslesenChapterExtractor
    reverse = False
    pattern = rf"{BASE_PATTERN}/read/manga/([^/?#]+)"
    example = "https://danke.moe/read/manga/TITLE/"

    def chapters(self, page):
        results = []

        manga = self._manga_info(self.groups[0]).copy()
        manga["lang"] = util.NONE
        manga["language"] = util.NONE

        base = f"{self.root}/read/manga/{manga['slug']}/"
        for ch, data in manga.pop("chapters").items():

            if "." in ch:
                chapter, sep, minor = ch.rpartition(".")
                ch = ch.replace('.', '-')
                data["chapter"] = text.parse_int(chapter)
                data["chapter_minor"] = sep + minor
            else:
                data["chapter"] = text.parse_int(ch)
                data["chapter_minor"] = ""

            results.append((f"{base}{ch}/1/", {**manga, **data}))

        return results
