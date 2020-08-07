# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.mangareader.net/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache
import json


class MangareaderBase():
    """Base class for mangareader extractors"""
    category = "mangareader"
    root = "https://www.mangareader.net"

    @memcache(keyarg=1)
    def _manga_info(self, path, page=None):
        if not page:
            page = self.request(self.root + path).text
        extr = text.extract_from(page)
        data = {
            "manga"   : text.unescape(extr('class="name">', '<')),
            "release" : text.unescape(extr('Year of Release :</td><td>', '<')),
            "author"  : text.unescape(text.unescape(extr(
                'Author :</td><td>', '<'))),
            "artist"  : text.unescape(text.unescape(extr(
                'Artist :</td><td>', '<'))),
            "lang"    : "en",
            "language": "English",
        }

        extr('<table', '>')
        chapters = []
        while True:
            url = extr('</i> <a href="', '"')
            if not url:
                return chapters
            chapter = {
                "chapter": text.parse_int(url.rpartition("/")[2]),
                "title"  : text.unescape(extr("</a> : ", "<")),
                "date"   : extr("<td>", "<"),
            }
            chapter.update(data)
            chapters.append((self.root + url, chapter))


class MangareaderChapterExtractor(MangareaderBase, ChapterExtractor):
    """Extractor for manga-chapters from mangareader.net"""
    archive_fmt = "{manga}_{chapter}_{page}"
    pattern = r"(?:https?://)?(?:www\.)?mangareader\.net((/[^/?&#]+)/(\d+))"
    test = (("https://www.mangareader.net"
             "/karate-shoukoushi-kohinata-minoru/11"), {
        "url": "45ece5668d1e9f65cf2225237d78de58660b54e4",
        "keyword": "133e3e2f7c0529a35bbb16149e34c40546f8dfd6",
    })

    def __init__(self, match):
        ChapterExtractor.__init__(self, match)
        _, self.path, self.chapter = match.groups()

    def metadata(self, page):
        chapter = text.parse_int(self.chapter)
        return self._manga_info(self.path)[chapter-1][1]

    def images(self, page):
        data = json.loads(text.extract(
            page, 'document["mj"]=', '</script>')[0])
        return [
            (text.ensure_http_scheme(img["u"]), {
                "width" : text.parse_int(img["w"]),
                "height": text.parse_int(img["h"]),
            })
            for img in data["im"]
        ]


class MangareaderMangaExtractor(MangareaderBase, MangaExtractor):
    """Extractor for manga from mangareader.net"""
    chapterclass = MangareaderChapterExtractor
    reverse = False
    pattern = r"(?:https?://)?(?:www\.)?mangareader\.net(/[^/?&#]+)/?$"
    test = ("https://www.mangareader.net/mushishi", {
        "url": "bc203b858b4ad76e5d77e39118a7be0350e357da",
        "keyword": "031b3ea085921c552de017ecbb9b906e462229c9",
    })

    def chapters(self, page):
        path = self.manga_url[len(self.root):]
        return self._manga_info(path, page)
