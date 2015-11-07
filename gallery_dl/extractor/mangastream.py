# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from https://www.mangastream.com/"""

from .common import AsynchronousExtractor, Message
from .. import text
import os.path

info = {
    "category": "mangastream",
    "extractor": "MangaStreamExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03}{chapter-minor} - {title}"],
    "filename": "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?readms\.com/r/([^/]*/(\d+)([^/]*)?/(\d+))",
    ],
}

class MangaStreamExtractor(AsynchronousExtractor):

    url_base = "https://readms.com/r/"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.part, self.chapter, self.ch_minor,self.ch_id = match.groups()

    def items(self):
        page = self.request(self.url_base + self.part).text
        data = self.get_job_metadata(page)
        next_url = None
        yield Message.Version, 1
        yield Message.Directory, data
        for i in range(int(data["count"])):
            if next_url:
                page = self.request(next_url).text
            next_url, image_url = self.get_page_metadata(page)
            filename = text.unquote(text.filename_from_url(image_url))
            name, ext = os.path.splitext(filename)
            data["page"] = i+1
            data["name"] = name
            data["extension"] = ext[1:]
            yield Message.Url, image_url, data.copy()

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "category": info["category"],
            "chapter": self.chapter,
            "chapter-minor": self.ch_minor,
            "chapter-id": self.ch_id,
            "lang": "en",
            "language": "English",
        }
        data, _ = text.extract_all(page, (
            ('manga', 'visible-tablet">', '</span>'),
            ('title', 'visible-tablet"> - ', '</span>'),
            ('count', 'Last Page (', ')'),
        ), values=data)
        return data

    def get_page_metadata(self, page):
        """Collect next url, image-url and metadata for one manga-page"""
        nurl, pos = text.extract(page, '<div class="page">\n<a href="', '"')
        iurl, pos = text.extract(page, '<img id="manga-page" src="', '"', pos)
        return nurl, iurl
