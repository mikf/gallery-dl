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


BASE_PATTERN = r"(?:https?://)?(?:www\.)?hiperdex\.(?:com|net|info)"


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
    pattern = BASE_PATTERN + r"(/manga/([^/?&#]+)/([^/?&#]+))"
    test = (
        ("https://hiperdex.com/manga/domestic-na-kanojo/154-5/", {
            "pattern": r"https://hiperdex.(com|net|info)/wp-content/uploads"
                       r"/WP-manga/data/manga_\w+/[0-9a-f]{32}/\d+\.webp",
            "count": 9,
            "keyword": {
                "artist" : "Sasuga Kei",
                "author" : "Sasuga Kei",
                "chapter": 154,
                "chapter_minor": ".5",
                "description": "re:Natsuo Fujii is in love with his teacher, ",
                "genre"  : list,
                "manga"  : "Domestic na Kanojo",
                "release": 2014,
                "score"  : float,
                "type"   : "Manga",
            },
        }),
        ("https://hiperdex.net/manga/domestic-na-kanojo/154-5/"),
        ("https://hiperdex.info/manga/domestic-na-kanojo/154-5/"),
    )

    def __init__(self, match):
        path, self.manga, self.chapter = match.groups()
        ChapterExtractor.__init__(self, match, self.root + path + "/")

    def metadata(self, _):
        return self.chapter_data(self.chapter)

    def images(self, page):
        return [
            (url.strip(), None)
            for url in re.findall(
                r'id="image-\d+"\s+(?:data-)?src="([^"]+)', page)
        ]


class HiperdexMangaExtractor(HiperdexBase, MangaExtractor):
    """Extractor for manga from hiperdex.com"""
    chapterclass = HiperdexChapterExtractor
    pattern = BASE_PATTERN + r"(/manga/([^/?&#]+))/?$"
    test = (
        ("https://hiperdex.com/manga/youre-not-that-special/", {
            "count": 51,
            "pattern": HiperdexChapterExtractor.pattern,
            "keyword": {
                "artist" : "Bolp",
                "author" : "Abyo4",
                "chapter": int,
                "chapter_minor": "",
                "description": "re:I didn’t think much of the creepy girl in ",
                "genre"  : list,
                "manga"  : "You’re Not That Special!",
                "release": 2019,
                "score"  : float,
                "status" : "Completed",
                "type"   : "Manhwa",
            },
        }),
        ("https://hiperdex.net/manga/youre-not-that-special/"),
        ("https://hiperdex.info/manga/youre-not-that-special/"),
    )

    def __init__(self, match):
        path, self.manga = match.groups()
        MangaExtractor.__init__(self, match, self.root + path + "/")

    def chapters(self, page):
        self.manga_data(self.manga, page)
        results = []

        shortlink = text.extract(page, "rel='shortlink' href='", "'")[0]
        data = {
            "action": "manga_get_chapters",
            "manga" : shortlink.rpartition("=")[2],
        }
        url = self.root + "/wp-admin/admin-ajax.php"
        page = self.request(url, method="POST", data=data).text

        for url in text.extract_iter(page, 'href="', '"', 320):
            chapter = url.rpartition("/")[2]
            results.append((url, self.chapter_data(chapter)))

        return results


class HiperdexArtistExtractor(HiperdexBase, MangaExtractor):
    """Extractor for an artists's manga on hiperdex.com"""
    subcategory = "artist"
    categorytransfer = False
    chapterclass = HiperdexMangaExtractor
    reverse = False
    pattern = BASE_PATTERN + r"(/manga-a(?:rtist|uthor)/([^/?&#]+))"
    test = (
        ("https://hiperdex.com/manga-artist/beck-ho-an/"),
        ("https://hiperdex.net/manga-artist/beck-ho-an/"),
        ("https://hiperdex.info/manga-artist/beck-ho-an/"),
        ("https://hiperdex.com/manga-author/viagra/", {
            "pattern": HiperdexMangaExtractor.pattern,
            "count": ">= 6",
        }),
    )

    def __init__(self, match):
        MangaExtractor.__init__(self, match, self.root + match.group(1) + "/")

    def chapters(self, page):
        results = []
        for info in text.extract_iter(page, 'id="manga-item-', '<img'):
            url = text.extract(info, 'href="', '"')[0]
            results.append((url, {}))
        return results
