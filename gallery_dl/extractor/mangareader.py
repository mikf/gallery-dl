# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangareader.net/"""

from .common import AsynchronousExtractor, MangaExtractor, Message
from .. import text, util


class MangareaderBase():
    """Base class for mangareader extractors"""
    category = "mangareader"
    root = "http://www.mangareader.net"

    @staticmethod
    def parse_page(page, data):
        """Parse metadata on 'page' and add it to 'data'"""
        text.extract_all(page, (
            ("manga"  , '<h2 class="aname">', '</h2>'),
            ("release", '>Year of Release:</td>\n<td>', '</td>'),
            ('author' , '>Author:</td>\n<td>', '</td>'),
            ('artist' , '>Artist:</td>\n<td>', '</td>'),
        ), values=data)
        data["manga"] = data["manga"].strip()
        data["author"] = text.unescape(data["author"])
        data["artist"] = text.unescape(data["artist"])
        return data


class MangareaderMangaExtractor(MangareaderBase, MangaExtractor):
    """Extractor for manga from mangareader.net"""
    pattern = [r"(?:https?://)?((?:www\.)?mangareader\.net/[^/?&#]+)/?$"]
    reverse = False
    test = [("http://www.mangareader.net/mushishi", {
        "url": "249042420b67a07b32e7f6be4c7410b6d810b808",
        "keyword": "031b3ea085921c552de017ecbb9b906e462229c9",
    })]

    def chapters(self, page):
        results = []
        data = self.parse_page(page, {"lang": "en", "language": "English"})

        needle = '<div class="chico_manga"></div>\n<a href="'
        pos = page.index('<div id="chapterlist">')
        while True:
            url, pos = text.extract(page, needle, '"', pos)
            if not url:
                return results
            data["title"], pos = text.extract(page, '</a> : ', '</td>', pos)
            data["date"] , pos = text.extract(page, '<td>', '</td>', pos)
            data["chapter"] = util.safe_int(url.rpartition("/")[2])
            results.append((self.root + url, data.copy()))


class MangareaderChapterExtractor(MangareaderBase, AsynchronousExtractor):
    """Extractor for manga-chapters from mangareader.net"""
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{title:?: //}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [
        (r"(?:https?://)?(?:www\.)?mangareader\.net((/[^/?&#]+)/(\d+))"),
        (r"(?:https?://)?(?:www\.)?mangareader\.net"
         r"(/\d+-\d+-\d+(/[^/]+)/chapter-(\d+)\.html)"),
    ]
    test = [(("http://www.mangareader.net/"
              "karate-shoukoushi-kohinata-minoru/11"), {
        "url": "84ffaab4c027ef9022695c53163c3aeabd07ca58",
        "keyword": "2038e6a780a0028eee0067985b55debb1d4a6aab",
    })]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.part, self.url_title, self.chapter = match.groups()

    def items(self):
        page = self.request(self.root + self.part).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"] in range(1, data["count"]+1):
            next_url, image_url, image_data = self.get_page_metadata(page)
            image_data.update(data)
            yield Message.Url, image_url, image_data
            if next_url:
                page = self.request(next_url).text

    def get_job_metadata(self, chapter_page):
        """Collect metadata for extractor-job"""
        page = self.request(self.root + self.url_title).text
        data = self.parse_page(page, {
            "chapter": util.safe_int(self.chapter),
            "lang": "en",
            "language": "English",
        })
        text.extract_all(page, (
            ('title', ' ' + self.chapter + '</a> : ', '</td>'),
            ('date', '<td>', '</td>'),
        ), page.index('<div id="chapterlist">'), data)
        data["count"] = util.safe_int(text.extract(
            chapter_page, '</select> of ', '<')[0]
        )
        return data

    def get_page_metadata(self, page):
        """Collect next url, image-url and metadata for one manga-page"""
        extr = text.extract
        width = None
        test , pos = extr(page, "document['pu']", '')
        if test is None:
            return None, None, None
        if page.find("document['imgwidth']", pos, pos+200) != -1:
            width , pos = extr(page, "document['imgwidth'] = ", ";", pos)
            height, pos = extr(page, "document['imgheight'] = ", ";", pos)
        _  , pos = extr(page, '<div id="imgholder">', '')
        url, pos = extr(page, ' href="', '"', pos)
        if width is None:
            width , pos = extr(page, '<img id="img" width="', '"', pos)
            height, pos = extr(page, ' height="', '"', pos)
        image, pos = extr(page, ' src="', '"', pos)
        return self.root + url, image, text.nameext_from_url(image, {
            "width": util.safe_int(width),
            "height": util.safe_int(height),
        })
