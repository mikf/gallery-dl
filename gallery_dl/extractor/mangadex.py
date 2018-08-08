# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangadex.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
import json


class MangadexExtractor():
    """Base class for mangadex extractors"""
    category = "mangadex"
    root = "https://mangadex.org"

    # mangadex-to-iso639-1 codes
    iso639_map = {
        "br": "pt",
        "ct": "ca",
        "gb": "en",
        "vn": "vi",
    }


class MangadexChapterExtractor(MangadexExtractor, ChapterExtractor):
    """Extractor for manga-chapters from mangadex.org"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = [r"(?:https?://)?(?:www\.)?mangadex\.(?:org|com)/chapter/(\d+)"]
    test = [
        ("https://mangadex.org/chapter/122094", {
            "keyword": "1fa2ed74f8da89f7b9d403f18d90a6f4df57a55f",
            "content": "7ab3bef5caccb62b881f8e6e70359d3c7be8137f",
        }),
        # oneshot
        ("https://mangadex.org/chapter/138086", {
            "count": 64,
            "keyword": "f3cd8a938bfe44a8ad22d35c84f92d724bc5d66f",
        }),
    ]

    def __init__(self, match):
        url = "{}/api/chapter/{}".format(self.root, match.group(1))
        ChapterExtractor.__init__(self, url)
        self.data = None

    def get_metadata(self, page):
        self.data = data = json.loads(page)
        chapter, sep, minor = data["chapter"].partition(".")

        url = "{}/api/manga/{}".format(self.root, data["manga_id"])
        mdata = self.request(url).json()

        return {
            "manga": mdata["manga"]["title"],
            "manga_id": data["manga_id"],
            "title": text.unescape(data["title"]),
            "volume": text.parse_int(data["volume"]),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": data["id"],
            "group": mdata["chapter"][str(data["id"])]["group_name"],
            "lang": util.language_to_code(data["lang_name"]),
            "language": data["lang_name"],
        }

    def get_images(self, _):
        base = self.data["server"] + self.data["hash"] + "/"
        return [
            (base + page, None)
            for page in self.data["page_array"]
        ]


class MangadexMangaExtractor(MangadexExtractor, MangaExtractor):
    """Extractor for manga from mangadex.org"""
    pattern = [r"(?:https?://)?(?:www\.)?mangadex\.(?:org|com)/manga/(\d+)"]
    test = [
        ("https://mangadex.org/manga/2946/souten-no-koumori", {
            "count": ">= 1",
            "keywords": {
                "manga": "Souten no Koumori",
                "manga_id": 2946,
                "title": "Oneshot",
                "volume": 0,
                "chapter": 0,
                "chapter_minor": "",
                "chapter_id": int,
                "group": str,
                "date": int,
                "lang": str,
                "language": str,
            },
        }),
        ("https://mangadex.org/manga/13318/dagashi-kashi/chapters/2/", {
            "count": ">= 100",
        }),
    ]
    reverse = False

    def __init__(self, match):
        self.manga_id = match.group(1)
        url = "{}/api/manga/{}".format(self.root, self.manga_id)
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        data = json.loads(page)
        manga = data["manga"]

        results = []
        for chid, info in data["chapter"].items():
            chapter, sep, minor = info["chapter"].partition(".")
            lang = self.iso639_map.get(info["lang_code"], info["lang_code"])

            results.append((self.root + "/chapter/" + chid, {
                "manga": manga["title"],
                "manga_id": text.parse_int(self.manga_id),
                "artist": manga["artist"],
                "author": manga["author"],
                "title": text.unescape(info["title"]),
                "volume": text.parse_int(info["volume"]),
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": text.parse_int(chid),
                "group": text.unescape(info["group_name"]),
                "date": info["timestamp"],
                "lang": lang,
                "language": util.code_to_language(lang),
            }))

        results.sort(key=lambda x: (x[1]["chapter"], x[1]["chapter_minor"]))
        return results
