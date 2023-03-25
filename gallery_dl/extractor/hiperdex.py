# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hiperdex.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache
import re

BASE_PATTERN = (r"((?:https?://)?(?:www\.)?"
                r"(?:1st)?hiperdex\d?\.(?:com|net|info))")


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
                "<title>", "<").rpartition(" - ")[0].strip()),
            "url"    : text.unescape(extr(
                'property="og:url" content="', '"')),
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
        if chapter.startswith("chapter-"):
            chapter = chapter[8:]
        chapter, _, minor = chapter.partition("-")
        data = {
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": "." + minor if minor and minor != "end" else "",
        }
        data.update(self.manga_data(self.manga.lower()))
        return data


class HiperdexChapterExtractor(HiperdexBase, ChapterExtractor):
    """Extractor for manga chapters from hiperdex.com"""
    pattern = BASE_PATTERN + r"(/manga/([^/?#]+)/([^/?#]+))"
    test = (
        ("https://hiperdex.com/manga/domestic-na-kanojo/154-5/", {
            "pattern": r"https://(1st)?hiperdex\d?.(com|net|info)"
                       r"/wp-content/uploads/WP-manga/data"
                       r"/manga_\w+/[0-9a-f]{32}/\d+\.webp",
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
        ("https://1sthiperdex.com/manga/domestic-na-kanojo/154-5/"),
        ("https://hiperdex2.com/manga/domestic-na-kanojo/154-5/"),
        ("https://hiperdex.net/manga/domestic-na-kanojo/154-5/"),
        ("https://hiperdex.info/manga/domestic-na-kanojo/154-5/"),
    )

    def __init__(self, match):
        root, path, self.manga, self.chapter = match.groups()
        self.root = text.ensure_http_scheme(root)
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
    pattern = BASE_PATTERN + r"(/manga/([^/?#]+))/?$"
    test = (
        ("https://hiperdex.com/manga/1603231576-youre-not-that-special/", {
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
        ("https://hiperdex.com/manga/youre-not-that-special/"),
        ("https://1sthiperdex.com/manga/youre-not-that-special/"),
        ("https://hiperdex2.com/manga/youre-not-that-special/"),
        ("https://hiperdex.net/manga/youre-not-that-special/"),
        ("https://hiperdex.info/manga/youre-not-that-special/"),
    )

    def __init__(self, match):
        root, path, self.manga = match.groups()
        self.root = text.ensure_http_scheme(root)
        MangaExtractor.__init__(self, match, self.root + path + "/")

    def chapters(self, page):
        data = self.manga_data(self.manga, page)
        self.manga_url = url = data["url"]

        url = self.manga_url + "ajax/chapters/"
        headers = {
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.root,
            "Referer": self.manga_url,
        }
        html = self.request(url, method="POST", headers=headers).text

        results = []
        for item in text.extract_iter(
                html, '<li class="wp-manga-chapter', '</li>'):
            url = text.extr(item, 'href="', '"')
            chapter = url.rstrip("/").rpartition("/")[2]
            results.append((url, self.chapter_data(chapter)))
        return results


class HiperdexArtistExtractor(HiperdexBase, MangaExtractor):
    """Extractor for an artists's manga on hiperdex.com"""
    subcategory = "artist"
    categorytransfer = False
    chapterclass = HiperdexMangaExtractor
    reverse = False
    pattern = BASE_PATTERN + r"(/manga-a(?:rtist|uthor)/(?:[^/?#]+))"
    test = (
        ("https://1sthiperdex.com/manga-artist/beck-ho-an/"),
        ("https://hiperdex.net/manga-artist/beck-ho-an/"),
        ("https://hiperdex2.com/manga-artist/beck-ho-an/"),
        ("https://hiperdex.info/manga-artist/beck-ho-an/"),
        ("https://hiperdex.com/manga-author/viagra/", {
            "pattern": HiperdexMangaExtractor.pattern,
            "count": ">= 6",
        }),
    )

    def __init__(self, match):
        self.root = text.ensure_http_scheme(match.group(1))
        MangaExtractor.__init__(self, match, self.root + match.group(2) + "/")

    def chapters(self, page):
        results = []
        for info in text.extract_iter(page, 'id="manga-item-', '<img'):
            url = text.extr(info, 'href="', '"')
            results.append((url, {}))
        return results
