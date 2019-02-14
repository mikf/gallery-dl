# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://komikcast.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, cloudflare
import re


class KomikcastBase():
    """Base class for komikcast extractors"""
    category = "komikcast"
    root = "https://komikcast.com"

    request = cloudflare.request_func

    @staticmethod
    def parse_chapter_string(chapter_string, data=None):
        """Parse 'chapter_string' value and add its info to 'data'"""
        if not data:
            data = {}

        match = re.match(
            r"(?:(.*) Chapter )?0*(\d+)([^ ]*)(?: (?:- )?(.+))?",
            text.unescape(chapter_string),
        )
        manga, chapter, data["chapter_minor"], title = match.groups()

        if manga:
            data["manga"] = manga.partition(" Chapter ")[0]
        if title and title.lower() != "bahasa indonesia":
            data["title"] = title.strip()
        else:
            data["title"] = ""
        data["chapter"] = text.parse_int(chapter)
        data["lang"] = "id"
        data["language"] = "Indonesian"

        return data


class KomikcastChapterExtractor(KomikcastBase, ChapterExtractor):
    """Extractor for manga-chapters from komikcast.com"""
    pattern = r"(?:https?://)?(?:www\.)?komikcast\.com(/chapter/[^/?&#]+/)"
    test = (
        (("https://komikcast.com/chapter/"
          "apotheosis-chapter-02-2-bahasa-indonesia/"), {
            "url": "2a108bf8a96753266610afef625d248f858e13f3",
            "keyword": "5c677ec86957f3bdad2bd5102a69a872a11c0f92",
        }),
        (("https://komikcast.com/chapter/"
          "tonari-no-kashiwagi-san-chapter-18b/"), {
            "url": "aff90dd21dbb945a726778b10bdef522af7c42fe",
            "keyword": "2469acd77c635fedcc131b5d40e7acc36e4674ad",
        }),
    )

    def metadata(self, page):
        info = text.extract(page, '<b>', "</b>")[0]
        return self.parse_chapter_string(info)

    @staticmethod
    def images(page):
        readerarea = text.extract(
            page, '<div id="readerarea">', '<div class="navig">')[0]
        return [
            (text.unescape(url), {
                "width": text.parse_int(width),
                "height": text.parse_int(height),
            })
            for url, width, height in re.findall(
                r"<img[^>]*? src=[\"']([^\"']+)[\"']"
                r"(?:\s+data-original-width=[\"']([^\"']+)[\"'])?"
                r"(?:\s+data-original-height=[\"']([^\"']+)[\"'])?",
                readerarea
            )
            if "/Banner-" not in url
        ]


class KomikcastMangaExtractor(KomikcastBase, MangaExtractor):
    """Extractor for manga from komikcast.com"""
    chapterclass = KomikcastChapterExtractor
    pattern = (r"(?:https?://)?(?:www\.)?komikcast\.com"
               r"(/(?:komik/)?[^/?&#]+)/?$")
    test = (
        ("https://komikcast.com/komik/090-eko-to-issho/", {
            "url": "dc798d107697d1f2309b14ca24ca9dba30c6600f",
            "keyword": "3db7e23e3c108031608fbbeb9334badecd967f95",
        }),
        ("https://komikcast.com/tonari-no-kashiwagi-san/"),
    )

    def chapters(self, page):
        results = []
        data = self.get_metadata(page)

        for item in text.extract_iter(
                page, '<span class="leftoff"><a href="', '</a>'):
            url, _, chapter_string = item.rpartition('">Chapter ')
            self.parse_chapter_string(chapter_string, data)
            results.append((url, data.copy()))
        return results

    @staticmethod
    def get_metadata(page):
        """Return a dict with general metadata"""
        manga , pos = text.extract(page, "<title>", "</title>")
        author, pos = text.extract(page, "<th>Author</th><td>", "</td>", pos)
        genres, pos = text.extract(page, "<th>Genres </th><td>", "</td>", pos)
        mtype , pos = text.extract(page, "<th>Type </th><td>", "</td>", pos)

        return {
            "manga": text.unescape(manga.rpartition(" - ")[0]),
            "author": text.unescape(author),
            "genres": text.remove_html(genres).replace(" , ", ", "),
            "type": text.remove_html(mtype),
        }
