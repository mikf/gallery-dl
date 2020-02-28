# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hiperdex.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache
import re


class HiperdexBase():
    """Base class for hiperdex extractors"""
    category = "hiperdex"
    root = "https://hiperdex.com"

    @memcache(keyarg=1)
    def manga_data(self, manga, page=None):
        if not page:
            url = "{}/manga/{}/".format(self.root, manga)
            page = self.request(url).text
        extr = text.extract_from(page)

        return {
            "manga"  : text.unescape(extr(
                "<title>", "<").rpartition("&")[0].strip()),
            "score"  : text.parse_float(extr(
                'id="averagerate">', '<')),
            "author" : text.remove_html(extr(
                'class="author-content">', '</div>')),
            "artist" : text.remove_html(extr(
                'class="artist-content">', '</div>')),
            "genre"  : text.split_html(extr(
                'class="genres-content">', '</div>'))[::2],
            "type"   : extr(
                'class="summary-content">', '<').strip(),
            "release": text.parse_int(text.remove_html(extr(
                'class="summary-content">', '</div>'))),
            "status" : extr(
                'class="summary-content">', '<').strip(),
            "description": text.remove_html(text.unescape(extr(
                'class="description-summary">', '</div>'))),
            "language": "English",
            "lang"    : "en",
        }

    def chapter_data(self, chapter):
        chapter, _, minor = chapter.partition("-")
        data = {
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": "." + minor if minor and minor != "end" else "",
        }
        data.update(self.manga_data(self.manga.lower()))
        return data


class HiperdexChapterExtractor(HiperdexBase, ChapterExtractor):
    """Extractor for manga chapters from hiperdex.com"""
    pattern = (r"(?:https?://)?(?:www\.)?hiperdex\.com"
               r"(/manga/([^/?&#]+)/([^/?&#]+))")
    test = ("https://hiperdex.com/manga/domestic-na-kanojo/154-5/", {
        "url": "111bc3ee14ce91d78c275770ef63b56c9ac15d8d",
        "keyword": {
            "artist" : "Sasuga Kei",
            "author" : "Sasuga Kei",
            "chapter": 154,
            "chapter_minor": ".5",
            "description": "re:Natsuo Fujii is in love with his teacher, Hina",
            "genre"  : list,
            "manga"  : "Domestic na Kanojo",
            "release": 2014,
            "score"  : float,
            "type"   : "Manga",
        },
    })

    def __init__(self, match):
        path, self.manga, self.chapter = match.groups()
        ChapterExtractor.__init__(self, match, self.root + path + "/")

    def metadata(self, _):
        return self.chapter_data(self.chapter)

    def images(self, page):
        return [
            (url.strip(), None)
            for url in re.findall(r'id="image-\d+"\s+src="([^"]+)', page)
        ]


class HiperdexMangaExtractor(HiperdexBase, MangaExtractor):
    """Extractor for manga from hiperdex.com"""
    chapterclass = HiperdexChapterExtractor
    pattern = r"(?:https?://)?(?:www\.)?hiperdex\.com(/manga/([^/?&#]+))/?$"
    test = ("https://hiperdex.com/manga/youre-not-that-special/", {
        "count": 51,
        "pattern": HiperdexChapterExtractor.pattern,
        "keyword": {
            "artist" : "Bolp",
            "author" : "Abyo4",
            "chapter": int,
            "chapter_minor": "",
            "description": "re:I didn’t think much of the creepy girl in ",
            "genre"  : list,
            "manga"  : "You're Not That Special!",
            "release": 2019,
            "score"  : float,
            "status" : "Completed",
            "type"   : "Manhwa",
        },
    })

    def __init__(self, match):
        path, self.manga = match.groups()
        MangaExtractor.__init__(self, match, self.root + path + "/")

    def chapters(self, page):
        self.manga_data(self.manga, page)
        results = []
        last = None

        page = text.extract(page, 'class="page-content-listing', '</ul>')[0]
        for match in HiperdexChapterExtractor.pattern.finditer(page):
            path = match.group(1)
            if last != path:
                last = path
                results.append((
                    self.root + path,
                    self.chapter_data(path.rpartition("/")[2]),
                ))

        return results
