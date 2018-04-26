# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.hbrowse.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import json


class HbrowseExtractor():
    """Base class for hbrowse extractors"""
    category = "hbrowse"
    root = "http://www.hbrowse.com"

    @staticmethod
    def parse_page(page, data):
        """Parse metadata on 'page' and add it to 'data'"""
        text.extract_all(page, (
            ('manga' , '<td class="listLong">', '</td>'),
            ('artist', '<td class="listLong">', '</td>'),
            ('total' , '<td class="listLong">', ' '),
            ('origin', '<td class="listLong">', '</td>'),
        ), values=data)

        data["manga"] = text.unescape(data["manga"])
        data["total"] = text.parse_int(data["total"])
        data["artist"] = text.remove_html(data["artist"])
        data["origin"] = text.remove_html(data["origin"])
        return data


class HbrowseMangaExtractor(HbrowseExtractor, MangaExtractor):
    """Extractor for manga from hbrowse.com"""
    pattern = [r"(?:https?://)?((?:www\.)?hbrowse\.com/\d+)/?$"]
    reverse = False
    test = [("http://www.hbrowse.com/10363", {
        "url": "4d9def5df21c23f8c3d36de2076c189c02ea43bd",
        "keyword": "aa0c6ba9ba180f18861aa5d608ff7f1966e666f8",
    })]

    def chapters(self, page):
        results = []
        data = self.parse_page(page, {
            "manga_id": text.parse_int(
                self.url.rstrip("/").rpartition("/")[2])
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


class HbrowseChapterExtractor(HbrowseExtractor, ChapterExtractor):
    """Extractor for manga-chapters from hbrowse.com"""
    directory_fmt = ["{category}", "{manga_id} {manga}", "c{chapter:>05}"]
    filename_fmt = ("{category}_{manga_id}_{chapter:>05}_"
                    "{page:>03}.{extension}")
    archive_fmt = "{manga_id}_{chapter}_{page}"
    pattern = [r"(?:https?://)?(?:www\.)?hbrowse\.com/(\d+)/c(\d+)"]
    test = [("http://www.hbrowse.com/10363/c00000", {
        "url": "634f4800858913f097bc3b62a8fedaf74b5254bd",
        "keyword": "f37cafef404696312f5db6ccaaaf72737d309e2d",
        "content": "44578ebbe176c2c27434966aef22945787e2781e",
    })]

    def __init__(self, match):
        self.gid, self.chapter = match.groups()
        self.path = "/{}/c{}/".format(self.gid, self.chapter)
        ChapterExtractor.__init__(self, self.root + self.path)

    def get_metadata(self, page):
        return self.parse_page(page, {
            "manga_id": text.parse_int(self.gid),
            "chapter": text.parse_int(self.chapter)
        })

    def get_images(self, page):
        base = self.root + "/data" + self.path
        json_data = text.extract(page, ';list = ', ',"zzz"')[0] + "]"
        return [(base + name, None) for name in json.loads(json_data)]
