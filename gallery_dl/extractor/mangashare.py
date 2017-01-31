# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangashare.com/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text


class MangashareMangaExtractor(Extractor):
    """Extractor for mangas from mangashare.com"""
    category = "mangashare"
    subcategory = "manga"
    pattern = [r"(?:https?://)?read\.mangashare\.com/[^/]+$"]
    test = [("http://read.mangashare.com/Gantz", {
        "url": "c3b9153d99200ddd2fae0194dad903ccb815e9e7",
    })]

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


class MangashareChapterExtractor(AsynchronousExtractor):
    """Extractor for manga-chapters from mangashare.com"""
    category = "mangashare"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?read\.mangashare\.com/([^/]+/chapter-\d+)"]
    test = [("http://read.mangashare.com/Gantz/chapter-331/page001.html", {
        "url": "2980fb9548e809dea63d104bc514dcc33bdd9ef7",
        "keyword": "8afc1c2a3e64efa3d2b9ed2359885343f89bdfa9",
    })]
    url_fmt = "http://read.mangashare.com/{}/page{:>03}.html"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.part = match.group(1)

    def items(self):
        page = self.request(self.url_fmt.format(self.part, 1)).text
        data = self.get_job_metadata(page)
        urls = zip(
            range(1, int(data["count"])+1),
            self.get_image_urls(page),
        )
        yield Message.Version, 1
        yield Message.Directory, data.copy()
        for data["page"], url in urls:
            text.nameext_from_url(url, data)
            yield Message.Url, url, data.copy()

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
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
