# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://www.mangareader.net/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text


class MangareaderBase():
    """Base class for mangareader extractors"""
    category = "mangareader"
    root = "https://www.mangareader.net"

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
    test = [("https://www.mangareader.net/mushishi", {
        "url": "bc203b858b4ad76e5d77e39118a7be0350e357da",
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
            data["chapter"] = text.parse_int(url.rpartition("/")[2])
            results.append((self.root + url, data.copy()))


class MangareaderChapterExtractor(MangareaderBase, ChapterExtractor):
    """Extractor for manga-chapters from mangareader.net"""
    archive_fmt = "{manga}_{chapter}_{page}"
    pattern = [
        (r"(?:https?://)?(?:www\.)?mangareader\.net((/[^/?&#]+)/(\d+))"),
        (r"(?:https?://)?(?:www\.)?mangareader\.net"
         r"(/\d+-\d+-\d+(/[^/]+)/chapter-(\d+)\.html)"),
    ]
    test = [(("https://www.mangareader.net/"
              "karate-shoukoushi-kohinata-minoru/11"), {
        "url": "061cc92a07edf17bb991ce0821fa4c77a147a860",
        "keyword": "2893cfcd1916859fb498f3345f1929f868fe667f",
    })]

    def __init__(self, match):
        self.part, self.url_title, self.chapter = match.groups()
        ChapterExtractor.__init__(self, self.root + self.part)

    def get_metadata(self, chapter_page):
        """Collect metadata for extractor-job"""
        page = self.request(self.root + self.url_title).text
        data = self.parse_page(page, {
            "chapter": text.parse_int(self.chapter),
            "lang": "en",
            "language": "English",
        })
        text.extract_all(page, (
            ('title', ' ' + self.chapter + '</a> : ', '</td>'),
            ('date', '<td>', '</td>'),
        ), page.index('<div id="chapterlist">'), data)
        data["count"] = text.parse_int(text.extract(
            chapter_page, '</select> of ', '<')[0]
        )
        return data

    def get_images(self, page):
        while True:
            next_url, image_url, image_data = self.get_image_metadata(page)
            yield image_url, image_data

            if not next_url:
                return
            page = self.request(next_url).text

    def get_image_metadata(self, page):
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
        return self.root + url, image, {
            "width": text.parse_int(width),
            "height": text.parse_int(height),
        }
