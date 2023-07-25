# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://raw.senmanga.com/"""

from .common import ChapterExtractor
from .. import text


class SenmangaChapterExtractor(ChapterExtractor):
    """Extractor for manga chapters from raw.senmanga.com"""
    category = "senmanga"
    root = "https://raw.senmanga.com"
    pattern = r"(?:https?://)?raw\.senmanga\.com(/[^/?#]+/[^/?#]+)"
    test = (
        ("https://raw.senmanga.com/Bokura-wa-Minna-Kawaisou/37A/1", {
            "pattern": r"https://raw\.senmanga\.com/viewer"
                       r"/Bokura-wa-Minna-Kawaisou/37A/[12]",
            "url": "5f95140ff511d8497e2ec08fa7267c6bb231faec",
            "content": "556a16d5ca3441d7a5807b6b5ac06ec458a3e4ba",
            "keyword": {
                "chapter": "37A",
                "count": 2,
                "extension": "",
                "filename": "re:[12]",
                "lang": "ja",
                "language": "Japanese",
                "manga": "Bokura wa Minna Kawaisou",
                "page": int,
            },
        }),
        ("http://raw.senmanga.com/Love-Lab/2016-03/1", {
            "pattern": r"https://raw\.senmanga\.com/viewer"
                       r"/Love-Lab/2016-03/\d",
            "url": "8347b9f00c14b864dd3c19a1f5ae52adb2ef00de",
            "keyword": {
                "chapter": "2016-03",
                "count": 9,
                "extension": "",
                "filename": r"re:\d",
                "manga": "Renai Lab   恋愛ラボ",
            },
        }),
        ("https://raw.senmanga.com/akabane-honeko-no-bodyguard/1", {
            "pattern": r"https://i\d\.wp\.com/kumacdn.club/image-new-2/a"
                       r"/akabane-honeko-no-bodyguard/chapter-1"
                       r"/\d+-[0-9a-f]{13}\.jpg",
            "keyword": {
                "chapter": "1",
                "count": 65,
                "extension": "jpg",
                "filename": r"re:\d+-\w+",
                "manga": "Akabane Honeko no Bodyguard",
            },
        }),
        # no http scheme ()
        ("https://raw.senmanga.com/amama-cinderella/3", {
            "pattern": r"^https://kumacdn.club/image-new-2/a/amama-cinderella"
                       r"/chapter-3/.+\.jpg",
            "count": 30,
        }),
    )

    def _init(self):
        self.session.headers["Referer"] = self.gallery_url

        # select "All pages" viewer
        self.cookies.set("viewer", "1", domain="raw.senmanga.com")

    def metadata(self, page):
        title = text.extr(page, "<title>", "</title>")
        manga, _, chapter = title.partition(" - Chapter ")

        return {
            "manga"        : text.unescape(manga).replace("-", " "),
            "chapter"      : chapter.partition(" - Page ")[0],
            "chapter_minor": "",
            "lang"         : "ja",
            "language"     : "Japanese",
        }

    def images(self, page):
        return [
            (text.ensure_http_scheme(url), None)
            for url in text.extract_iter(
                page, '<img class="picture" src="', '"')
        ]
