# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangadex.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util, exception
from urllib.parse import urljoin
import json
import re


class MangadexExtractor():
    """Base class for mangadex extractors"""
    category = "mangadex"
    root = "https://mangadex.org"


class MangadexChapterExtractor(MangadexExtractor, ChapterExtractor):
    """Extractor for manga-chapters from mangadex.org"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = [r"(?:https?://)?(?:www\.)?mangadex\.(?:org|com)/chapter/(\d+)"]
    test = [
        ("https://mangadex.org/chapter/122094", {
            "keyword": "b4c83fe41f125eae745c2e00d29e087cc4eb78df",
            "content": "7ab3bef5caccb62b881f8e6e70359d3c7be8137f",
        }),
        # oneshot
        ("https://mangadex.org/chapter/138086", {
            "count": 64,
            "keyword": "9b1b7292f7dbcf10983fbdc34b8cdceeb47328ee",
        }),
        # NotFoundError
        ("https://mangadex.org/chapter/1", {
            "exception": exception.NotFoundError,
        })
    ]

    def __init__(self, match):
        self.chapter_id = match.group(1)
        url = self.root + "/chapter/" + self.chapter_id
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        if "title='Warning'" in page and " does not exist." in page:
            raise exception.NotFoundError("chapter")

        info    , pos = text.extract(page, '="og:title" content="', '"')
        manga_id, pos = text.extract(page, '/images/manga/', '.', pos)
        _       , pos = text.extract(page, ' id="jump_group"', '', pos)
        _       , pos = text.extract(page, ' selected ', '', pos)
        language, ___ = text.extract(page, " title='", "'", pos-100)
        group   , pos = text.extract(page, '>', '<', pos)

        info = text.unescape(info)
        match = re.match(
            r"(?:(?:Vol\. (\d+) )?Ch\. (\d+)([^ ]*)|(.*)) "
            r"\(([^)]+)\)",
            info)

        return {
            "manga": match.group(5),
            "manga_id": util.safe_int(manga_id),
            "volume": util.safe_int(match.group(1)),
            "chapter": util.safe_int(match.group(2)),
            "chapter_minor": match.group(3) or "",
            "chapter_id": util.safe_int(self.chapter_id),
            "chapter_string": info.replace(" - MangaDex", ""),
            "group": text.unescape(group),
            "lang": util.language_to_code(language),
            "language": language,
        }

    def get_images(self, page):
        dataurl , pos = text.extract(page, "var dataurl = '", "'")
        pagelist, pos = text.extract(page, "var page_array = [", "]", pos)
        server  , pos = text.extract(page, "var server = '", "'", pos)

        base = urljoin(self.root, server + dataurl + "/")

        return [
            (base + page, None)
            for page in json.loads(
                "[" + pagelist.replace("'", '"').rstrip(",") + "]"
            )
        ]


class MangadexMangaExtractor(MangadexExtractor, MangaExtractor):
    """Extractor for manga from mangadex.org"""
    pattern = [r"(?:https?://)?(?:www\.)?(mangadex\.(?:org|com)/manga/\d+)"]
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
                "contributor": str,
                "date": str,
                "views": int,
                "lang": str,
                "language": str,
            },
        }),
    ]
    scheme = "https"
    per_page = 100

    def chapters(self, page):
        results = []
        extr = text.extract
        num = 1

        manga = text.unescape(extr(
            page, '"og:title" content="', '"')[0].rpartition(" (")[0])
        manga_id = util.safe_int(extr(
            page, '/images/manga/', '.')[0])

        while True:
            before = len(results)

            for info in text.extract_iter(page, "<tr id=", "</tr>"):
                chid    , pos = extr(info, 'data-chapter-id="', '"')
                chapter , pos = extr(info, 'data-chapter-num="', '"', pos)
                volume  , pos = extr(info, 'data-volume-num="', '"', pos)
                title   , pos = extr(info, 'data-chapter-name="', '"', pos)
                language, pos = extr(info, " title='", "'", pos)
                group   , pos = extr(info, "<td>", "</td>", pos)
                user    , pos = extr(info, "<td>", "</td>", pos)
                views   , pos = extr(info, ">", "<", pos)
                date    , pos = extr(info, ' datetime="', '"', pos)

                chapter, sep, minor = chapter.partition(".")

                results.append((self.root + "/chapter/" + chid, {
                    "manga": manga,
                    "manga_id": util.safe_int(manga_id),
                    "title": text.unescape(title),
                    "volume": util.safe_int(volume),
                    "chapter": util.safe_int(chapter),
                    "chapter_minor": sep + minor,
                    "chapter_id": util.safe_int(chid),
                    "group": text.unescape(text.remove_html(group)),
                    "contributor": text.remove_html(user),
                    "views": util.safe_int(views),
                    "date": date,
                    "lang": util.language_to_code(language),
                    "language": language,
                }))

            if len(results) - before != self.per_page:
                return results

            num += 1
            page = self.request("{}/_/{}/".format(self.url, num)).text
