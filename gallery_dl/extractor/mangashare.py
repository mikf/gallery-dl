# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangashare.com/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text

class MangaShareMangaExtractor(Extractor):
    """Extract all manga-chapters from mangashare"""
    category = "mangashare"
    pattern = [r"(?:https?://)?read\.mangashare\.com/[^/]+$"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request(self.url).text
        return reversed(list(
            text.extract_iter(page, '<td class="datarow-0"><a href="', '"')
        ))


class MangaShareChapterExtractor(AsynchronousExtractor):
    """Extract a single manga-chapter from mangashare"""
    category = "mangashare"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?read\.mangashare\.com/([^/]+/chapter-\d+)"]
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

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "category": self.category,
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
