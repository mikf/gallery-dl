# -*- coding: utf-8 -*-

# Copyright 2020 Jake Mannens
# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.mangakakalot.gg/ and mirror sites"""

from .common import BaseExtractor, ChapterExtractor, MangaExtractor
from .. import text, util


class ManganeloExtractor(BaseExtractor):
    basecategory = "manganelo"


BASE_PATTERN = ManganeloExtractor.update({
    "nelomanga": {
        "root"   : "https://www.nelomanga.net",
        "pattern": r"(?:www\.)?nelomanga\.net",
    },
    "natomanga": {
        "root"   : "https://www.natomanga.com",
        "pattern": r"(?:www\.)?natomanga\.com",
    },
    "manganato": {
        "root"   : "https://www.manganato.gg",
        "pattern": r"(?:www\.)?manganato\.gg",
    },
    "mangakakalot": {
        "root"   : "https://www.mangakakalot.gg",
        "pattern": r"(?:www\.)?mangakakalot\.gg",
    },
})


class ManganeloChapterExtractor(ManganeloExtractor, ChapterExtractor):
    """Extractor for manganelo manga chapters"""
    pattern = rf"{BASE_PATTERN}(/manga/[^/?#]+/chapter-[^/?#]+)"
    example = "https://www.mangakakalot.gg/manga/MANGA_NAME/chapter-123"

    def __init__(self, match):
        ManganeloExtractor.__init__(self, match)
        self.page_url = self.root + self.groups[-1]

    def metadata(self, page):
        extr = text.extract_from(page)

        data = {
            "date"        : self.parse_datetime_iso(extr(
                '"datePublished": "', '"')[:19]),
            "date_updated": self.parse_datetime_iso(extr(
                '"dateModified": "', '"')[:19]),
            "manga_id"    : text.parse_int(extr("comic_id =", ";")),
            "chapter_id"  : text.parse_int(extr("chapter_id =", ";")),
            "manga"       : extr("comic_name =", ";").strip('" '),
            "lang"        : "en",
            "language"    : "English",
        }

        chapter_name = extr("chapter_name =", ";").strip('" ')
        chapter, sep, minor = chapter_name.rpartition(" ")[2].partition(".")
        data["chapter"] = text.parse_int(chapter)
        data["chapter_minor"] = sep + minor
        data["author"] = extr(". Author:", " already has ").strip()

        return data

    def images(self, page):
        extr = text.extract_from(page)
        cdns = util.json_loads(extr("var cdns =", ";"))[0]
        imgs = util.json_loads(extr("var chapterImages =", ";"))

        if cdns[-1] != "/":
            cdns += "/"

        return [
            (cdns + path, None)
            for path in imgs
        ]


class ManganeloMangaExtractor(ManganeloExtractor, MangaExtractor):
    """Extractor for manganelo manga"""
    chapterclass = ManganeloChapterExtractor
    pattern = rf"{BASE_PATTERN}(/manga/[^/?#]+)$"
    example = "https://www.mangakakalot.gg/manga/MANGA_NAME"

    def __init__(self, match):
        ManganeloExtractor.__init__(self, match)
        self.page_url = self.root + self.groups[-1]

    def chapters(self, page):
        extr = text.extract_from(page)

        manga = text.unescape(extr("<h1>", "<"))
        author = text.remove_html(extr("<li>Author(s) :", "</a>"))
        status = extr("<li>Status :", "<").strip()
        update = self.parse_datetime(extr(
            "<li>Last updated :", "<").strip(), "%b-%d-%Y %I:%M:%S %p")
        tags = text.split_html(extr(">Genres :", "</li>"))[::2]

        results = []
        for chapter in text.extract_iter(page, '<div class="row">', '</div>'):
            url, pos = text.extract(chapter, '<a href="', '"')
            title, pos = text.extract(chapter, '>', '</a>', pos)
            date, pos = text.extract(chapter, '<span title="', '"', pos)
            chapter, sep, minor = url.rpartition("/chapter-")[2].partition("-")

            if url[0] == "/":
                url = self.root + url
            results.append((url, {
                "manga"   : manga,
                "author"  : author,
                "status"  : status,
                "tags"    : tags,
                "date_updated": update,
                "chapter" : text.parse_int(chapter),
                "chapter_minor": (sep and ".") + minor,
                "title"   : title.partition(": ")[2],
                "date"    : self.parse_datetime(date, "%b-%d-%Y %H:%M"),
                "lang"    : "en",
                "language": "English",
            }))
        return results
