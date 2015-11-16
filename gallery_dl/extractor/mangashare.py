# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://www.mangashare.com/"""

from .common import AsynchronousExtractor, Message
from .. import text
import os

info = {
    "category": "mangashare",
    "extractor": "MangaShareExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03} - {title}"],
    "filename": "{manga}_c{chapter:>03}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?read\.mangashare\.com/([^/]+/chapter-\d+)",
    ],
}

class MangaShareExtractor(AsynchronousExtractor):

    url_fmt = "http://read.mangashare.com/{}/page{:>03}.html"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.part = match.group(1)

    def items(self):
        page = self.request(self.url_fmt.format(self.part, 1)).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data.copy()
        for i, url in zip(range(int(data["count"])), (self.get_image_urls(page))):
            data["page"] = i+1
            text.nameext_from_url(url, data)
            yield Message.Url, url, data.copy()

    @staticmethod
    def get_job_metadata(page):
        """Collect metadata for extractor-job"""
        data = {
            "category": info["category"],
            "lang": "en",
            "language": "English",
        }
        data, pos = text.extract_all(page, (
            ('manga'  , 'title="', '"'),
            ('chapter', 'selected="selected">', ' - '),
            ('title'  , '', '<'),
            (None     , 'Page 1', ''),
            (None     , '</select>', ''),
        ), values=data)
        data["count"] = text.extract(page, '>Page ', '<', pos-35)[0]
        return data

    def get_image_urls(self, page):
        """Yield all image-urls for this chapter"""
        pnum = 1
        while True:
            _  , pos = text.extract(page, '<div id="page">', '')
            url, pos = text.extract(page, '<img src="', '"', pos)
            yield url
            url, pos = text.extract(page, '<img src="', '"', pos)
            yield url
            pnum += 2
            page = self.request(self.url_fmt.format(self.part, pnum)).text
