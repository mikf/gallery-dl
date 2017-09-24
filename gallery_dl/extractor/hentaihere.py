# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://hentaihere.com/"""

from .common import MangaExtractor
from .. import text, util
from . import hentaicdn
import re


class HentaihereMangaExtractor(MangaExtractor):
    """Extractor for hmanga from hentaihere.com"""
    category = "hentaihere"
    pattern = [r"(?:https?://)?(?:www\.)?(hentaihere\.com/m/S\d+)/?$"]
    scheme = "https"
    test = [
        ("https://hentaihere.com/m/S13812", {
            "url": "d1ba6e28bb2162e844f8559c2b2725ba0a093559",
            "keyword": "13c1ce7e15cbb941f01c843b0e89adc993d939ac",
        }),
        ("https://hentaihere.com/m/S7608", {
            "url": "6c5239758dc93f6b1b4175922836c10391b174f7",
            "keyword": "675c7b7a4fa52cf569c283553bd16b4200a5cd36",
        }),
    ]

    def chapters(self, page):
        results = []
        manga_id = util.safe_int(
            self.url.rstrip("/").rpartition("/")[2][1:])
        manga, pos = text.extract(
            page, '<span itemprop="name">', '</span>')
        mtype, pos = text.extract(
            page, '<span class="mngType text-danger">[', ']</span>', pos)

        while True:
            url, pos = text.extract(
                page, '<li class="sub-chp clearfix">\n<a href="', '"', pos)
            if not url:
                return results
            chapter, pos = text.extract(page, 'title="Tagged: -">\n', '<', pos)
            chapter_id, pos = text.extract(page, '/C', '"', pos)
            chapter, _, title = text.unescape(chapter).strip().partition(" - ")
            results.append((url, {
                "manga_id": manga_id, "manga": manga, "type": mtype,
                "chapter_id": util.safe_int(chapter_id),
                "chapter": util.safe_int(chapter),
                "title": title, "lang": "en", "language": "English",
            }))


class HentaihereChapterExtractor(hentaicdn.HentaicdnChapterExtractor):
    """Extractor for a single manga chapter from hentaihere.com"""
    category = "hentaihere"
    pattern = [r"(?:https?://)?(?:www\.)?hentaihere\.com/m/S(\d+)/(\d+)"]
    test = [("https://hentaihere.com/m/S13812/1/1/", {
        "url": "964b942cf492b3a129d2fe2608abfc475bc99e71",
        "keyword": "a07753f655210525a80ff62607261715746f3273",
    })]

    def __init__(self, match):
        hentaicdn.HentaicdnChapterExtractor.__init__(self)
        self.gid, self.chapter = match.groups()
        self.url = "https://hentaihere.com/m/S{}/{}/1".format(
            self.gid, self.chapter
        )

    def get_job_metadata(self, page, images):
        title = text.extract(page, "<title>", "</title>")[0]
        chapter_id = text.extract(page, 'report/C', '"')[0]
        pattern = r"Page 1 \| (.+) \(([^)]+)\) - Chapter \d+: (.+) by (.+) at "
        match = re.match(pattern, title)
        return {
            "manga_id": self.gid,
            "manga": match.group(1),
            "type": match.group(2),
            "chapter_id": chapter_id,
            "chapter": self.chapter,
            "title": match.group(3),
            "author": match.group(4),
            "count": len(images),
            "lang": "en",
            "language": "English",
        }
