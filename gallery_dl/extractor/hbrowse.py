# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.hbrowse.com/"""

from .common import Extractor, MangaExtractor, Message
from .. import text
import json


class HbrowseMangaExtractor(MangaExtractor):
    """Extractor for manga from hbrowse.com"""
    category = "hbrowse"
    pattern = [r"(?:https?://)?((?:www\.)?hbrowse\.com/\d+)/?$"]
    reverse = False
    test = [("http://www.hbrowse.com/10363", {
        "url": "4d9def5df21c23f8c3d36de2076c189c02ea43bd",
    })]

    def chapters(self, page):
        needle = '<td class="listMiddle">\n<a class="listLink" href="'
        return list(text.extract_iter(page, needle, '"'))


class HbrowseChapterExtractor(Extractor):
    """Extractor for manga-chapters from hbrowse.com"""
    category = "hbrowse"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{gallery-id} {title}", "c{chapter:>05}"]
    filename_fmt = ("{category}_{gallery-id}_{chapter:>05}_"
                    "{num:>03}.{extension}")
    pattern = [r"(?:https?://)?(?:www\.)?hbrowse\.com/(\d+)/(c\d+)"]
    test = [("http://www.hbrowse.com/10363/c00000", {
        "url": "634f4800858913f097bc3b62a8fedaf74b5254bd",
        "keyword": "c7dc22a10699dee5cf466406fecee6ffa2e6277e",
        "content": "44578ebbe176c2c27434966aef22945787e2781e",
    })]
    url_base = "http://www.hbrowse.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid, self.chapter = match.groups()
        self.path = "/{}/{}/".format(self.gid, self.chapter)

    def items(self):
        page = self.request(self.url_base + self.path).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(self.get_image_urls(page), 1):
            data["num"] = num
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            'gallery-id': self.gid,
            "chapter": int(self.chapter[1:]),
        }
        return text.extract_all(page, (
            ('title'      , '<td class="listLong">', '</td>'),
            (None         , '<td class="listLong">', ''),
            ('artist'     , 'title="">', '<'),
            ('count-total', '<td class="listLong">', ' '),
            (None         , '<td class="listLong">', ''),
            ('origin'     , 'title="">', '<'),
        ), values=data)[0]

    def get_image_urls(self, page):
        """Yield all image-urls for a 'chapter'"""
        base = self.url_base + "/data" + self.path
        json_data = text.extract(page, ';list = ', ',"zzz"')[0] + "]"
        return [base + name for name in json.loads(json_data)]
