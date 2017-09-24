# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.hbrowse.com/"""

from .common import Extractor, MangaExtractor, Message
from .. import text, util
import json


class HbrowseExtractor(Extractor):
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
        data["total"] = util.safe_int(data["total"])
        data["artist"] = text.remove_html(data["artist"])
        data["origin"] = text.remove_html(data["origin"])
        return data


class HbrowseMangaExtractor(MangaExtractor, HbrowseExtractor):
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
            "manga_id": util.safe_int(
                self.url.rstrip("/").rpartition("/")[2])
        })

        pos = 0
        needle = '<td class="listMiddle">\n<a class="listLink" href="'
        while True:
            url, pos = text.extract(page, needle, '"', pos)
            if not url:
                return results
            title, pos = text.extract(page, '>View ', '<', pos)
            data["chapter"] = util.safe_int(url.rpartition("/")[2][1:])
            data["title"] = title
            results.append((url, data.copy()))


class HbrowseChapterExtractor(HbrowseExtractor):
    """Extractor for manga-chapters from hbrowse.com"""
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga_id} {manga}", "c{chapter:>05}"]
    filename_fmt = ("{category}_{manga_id}_{chapter:>05}_"
                    "{num:>03}.{extension}")
    pattern = [r"(?:https?://)?(?:www\.)?hbrowse\.com/(\d+)/c(\d+)"]
    test = [("http://www.hbrowse.com/10363/c00000", {
        "url": "634f4800858913f097bc3b62a8fedaf74b5254bd",
        "keyword": "730bd33de2a0a0fb4e0b6dcdafedcaeee1060047",
        "content": "44578ebbe176c2c27434966aef22945787e2781e",
    })]

    def __init__(self, match):
        HbrowseExtractor.__init__(self)
        self.gid, self.chapter = match.groups()
        self.path = "/{}/c{}/".format(self.gid, self.chapter)

    def items(self):
        page = self.request(self.root + self.path).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(self.get_image_urls(page), 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        return self.parse_page(page, {
            "manga_id": util.safe_int(self.gid),
            "chapter": util.safe_int(self.chapter)
        })

    def get_image_urls(self, page):
        """Yield all image-urls for a 'chapter'"""
        base = self.root + "/data" + self.path
        json_data = text.extract(page, ';list = ', ',"zzz"')[0] + "]"
        return [base + name for name in json.loads(json_data)]
