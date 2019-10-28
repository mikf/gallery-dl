# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.hbrowse.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, exception
import json


class HbrowseBase():
    """Base class for hbrowse extractors"""
    category = "hbrowse"
    root = "https://www.hbrowse.com"

    def parse_page(self, page, data):
        """Parse metadata on 'page' and add it to 'data'"""
        data, pos = text.extract_all(page, (
            ('manga' , '<td class="listLong">', '</td>'),
            ('artist', '<td class="listLong">', '</td>'),
            ('total' , '<td class="listLong">', ' '),
            ('origin', '<td class="listLong">', '</td>'),
        ), values=data)

        if not data["manga"] and "<b>Warning</b>" in page:
            msg = page.rpartition(">")[2].strip()
            raise exception.StopExtraction("Site is not accessible: '%s'", msg)

        tags = text.extract(page, 'class="listTable"', '</table>', pos)[0]

        data["manga"] = text.unescape(data["manga"])
        data["total"] = text.parse_int(data["total"])
        data["artist"] = text.remove_html(data["artist"])
        data["origin"] = text.remove_html(data["origin"])
        data["tags"] = list(text.extract_iter(tags, 'href="/browse/', '"'))
        return data


class HbrowseChapterExtractor(HbrowseBase, ChapterExtractor):
    """Extractor for manga-chapters from hbrowse.com"""
    directory_fmt = ("{category}", "{manga_id} {manga}", "c{chapter:>05}")
    filename_fmt = ("{category}_{manga_id}_{chapter:>05}_"
                    "{page:>03}.{extension}")
    archive_fmt = "{manga_id}_{chapter}_{page}"
    pattern = r"(?:https?://)?(?:www\.)?hbrowse\.com(/(\d+)/c(\d+))"
    test = ("https://www.hbrowse.com/10363/c00000", {
        "url": "6feefbc9f4b98e20d8425ddffa9dd111791dc3e6",
        "keyword": "274996f6c809e5250b6ff3abbc5147e29f89d9a5",
        "content": "44578ebbe176c2c27434966aef22945787e2781e",
    })

    def __init__(self, match):
        self.path, self.gid, self.chapter = match.groups()
        self.path += "/"
        ChapterExtractor.__init__(self, match)

    def metadata(self, page):
        return self.parse_page(page, {
            "manga_id": text.parse_int(self.gid),
            "chapter": text.parse_int(self.chapter)
        })

    def images(self, page):
        base = self.root + "/data" + self.path
        json_data = text.extract(page, ';list = ', ',"zzz"')[0] + "]"
        return [(base + name, None) for name in json.loads(json_data)]


class HbrowseMangaExtractor(HbrowseBase, MangaExtractor):
    """Extractor for manga from hbrowse.com"""
    chapterclass = HbrowseChapterExtractor
    reverse = False
    pattern = r"(?:https?://)?(?:www\.)?hbrowse\.com(/\d+)/?$"
    test = ("https://www.hbrowse.com/10363", {
        "url": "b89682bfb86c11d2af0dc47463804ec3ac4aadd6",
        "keyword": "4b15fda1858a69de1fbf5afddfe47dd893397312",
    })

    def chapters(self, page):
        results = []
        data = self.parse_page(page, {
            "manga_id": text.parse_int(
                self.manga_url.rstrip("/").rpartition("/")[2])
        })

        pos = 0
        needle = '<td class="listMiddle">\n<a class="listLink" href="'
        while True:
            url, pos = text.extract(page, needle, '"', pos)
            if not url:
                return results
            title, pos = text.extract(page, '>View ', '<', pos)
            data["chapter"] = text.parse_int(url.rpartition("/")[2][1:])
            data["title"] = title
            results.append((text.urljoin(self.root, url), data.copy()))
