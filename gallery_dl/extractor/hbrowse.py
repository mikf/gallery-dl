# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.hbrowse.com/"""

from .common import Extractor, Message
from .. import text
import os.path

info = {
    "category": "hbrowse",
    "extractor": "HbrowseExtractor",
    "directory": ["{category}", "{gallery-id} {title}"],
    "filename": "{category}_{gallery-id}_{num:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?hbrowse\.com/(\d+)/(c\d+)",
    ],
}

class HbrowseExtractor(Extractor):

    url_base = "http://www.hbrowse.com/thumbnails/"

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid, self.chapter = match.groups()

    def items(self):
        page = self.request(self.url_base + self.gid + "/" + self.chapter).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(self.get_image_urls(page), 1):
            data["num"] = num
            text.nameext_from_url(url, data)
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "category": info["category"],
            'gallery-id': self.gid,
            'chapter': int(self.chapter[1:]),
        }
        return text.extract_all(page, (
            ('title' , '<td class="listLong">', '</td>'),
            (None    , '<td class="listLong">', ''),
            ('artist', 'title="">', '<'),
            ('count' , '<td class="listLong">', ' '),
            (None    , '<td class="listLong">', ''),
            ('origin', 'title="">', '<'),
        ), values=data)[0]

    @staticmethod
    def get_image_urls(page):
        """Yield all image-urls for a 'chapter'"""
        base = "http://www.hbrowse.com/data/"
        pos = 0
        while True:
            url, pos = text.extract(page, base, '"', pos)
            if not url:
                return
            yield base + url.replace("zzz/", "")
