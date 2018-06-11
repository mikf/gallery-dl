# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangadex.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util, exception
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
            "keyword": "da1262219afe50dfe0098011366468fa507cc3c6",
            "content": "7ab3bef5caccb62b881f8e6e70359d3c7be8137f",
        }),
        # oneshot
        ("https://mangadex.org/chapter/138086", {
            "count": 64,
            "keyword": "1f6fb237a96cdf05b436ae2a37a4436e717bbb30",
        }),
        # NotFoundError
        ("https://mangadex.org/chapter/1", {
            "exception": exception.NotFoundError,
        })
    ]

    def __init__(self, match):
        url = self.root + "/chapter/" + match.group(1)
        ChapterExtractor.__init__(self, url)
        self.data = None

    def get_metadata(self, page):
        if "title='Warning'" in page and " does not exist." in page:
            raise exception.NotFoundError("chapter")

        info, pos = text.extract(page, '="og:title" content="', ' (')
        self.data = data = json.loads(
            text.extract(page, 'data-type="chapter">', '<', pos)[0])

        match = re.match(r"(?:[Vv]ol\. (\d+) )?[Cc]h\. ([^.]+)(\..+)?", info)
        if match:
            volume, chapter, minor = match.groups()
            chapter = chapter.rpartition(" ")[2]
        else:
            volume = chapter = minor = ""
        group = data["other_groups"][str(data["chapter_id"])]

        return {
            "manga": text.unescape(data["manga_title"]),
            "manga_id": data["manga_id"],
            "title": text.unescape(data["chapter_title"]),
            "volume": text.parse_int(volume),
            "chapter": text.parse_int(chapter),
            "chapter_minor": minor or "",
            "chapter_id": data["chapter_id"],
            "chapter_string": info,
            "group": text.unescape(group["group_name"]),
            "lang": util.language_to_code(group["lang_name"]),
            "language": group["lang_name"],
        }

    def get_images(self, _):
        base = self.data["server"] + self.data["dataurl"] + "/"
        base = text.urljoin(self.root, base)

        return [
            (base + page, None)
            for page in self.data["page_array"]
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
        ("https://mangadex.org/manga/13318/dagashi-kashi/chapters/2/", {
            "count": ">= 100",
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
        manga_id = text.parse_int(extr(
            page, '/images/manga/', '.')[0])

        while True:
            before = len(results)

            for info in text.extract_iter(page, '<tr id="chapter_', '</tr>'):
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
                chapter = chapter.rpartition(" ")[2]

                results.append((self.root + "/chapter/" + chid, {
                    "manga": manga,
                    "manga_id": text.parse_int(manga_id),
                    "title": text.unescape(title),
                    "volume": text.parse_int(volume),
                    "chapter": text.parse_int(chapter),
                    "chapter_minor": sep + minor,
                    "chapter_id": text.parse_int(chid),
                    "group": text.unescape(text.remove_html(group)),
                    "contributor": text.remove_html(user),
                    "views": text.parse_int(views),
                    "date": date,
                    "lang": util.language_to_code(language),
                    "language": language,
                }))

            if len(results) - before != self.per_page:
                return results

            num += 1
            page = self.request("{}/_/chapters/{}/".format(self.url, num)).text
