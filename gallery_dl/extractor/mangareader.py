# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangareader.net/"""

from .common import AsynchronousExtractor, Extractor, Message
from .. import text


class MangareaderBase():
    """Base class for mangareader extractors"""
    category = "mangareader"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    url_base = "http://www.mangareader.net"


class MangareaderMangaExtractor(MangareaderBase, Extractor):
    """Extractor for mangas from mangareader.net"""
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?mangareader\.net(/[^/]+)$"]
    test = [("http://www.mangareader.net/mushishi", {
        "url": "249042420b67a07b32e7f6be4c7410b6d810b808",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url_title = match.group(1)

    def items(self):
        yield Message.Version, 1
        url = self.url_base + self.url_title
        page = self.request(url).text
        needle = '<a href="' + self.url_title
        pos = page.index('<div id="readmangasum">')
        for chapter in text.extract_iter(page, needle, '"', pos):
            yield Message.Queue, url + chapter


class MangareaderChapterExtractor(MangareaderBase, AsynchronousExtractor):
    """Extractor for manga-chapters from mangareader.net"""
    subcategory = "chapter"
    pattern = [
        (r"(?:https?://)?(?:www\.)?mangareader\.net((/[^/]+)/(\d+))"),
        (r"(?:https?://)?(?:www\.)?mangareader\.net(/\d+-\d+-\d+(/[^/]+)/"
         r"chapter-(\d+).html)"),
    ]
    test = [(("http://www.mangareader.net/"
              "karate-shoukoushi-kohinata-minoru/11"), {
        "url": "84ffaab4c027ef9022695c53163c3aeabd07ca58",
        "keyword": "09b4ad57a082eb371dec027ccfc8ed1157c6eac6",
    })]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.part, self.url_title, self.chapter = match.groups()

    def items(self):
        page = self.request(self.url_base + self.part).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for i in range(1, int(data["count"])+1):
            next_url, image_url, image_data = self.get_page_metadata(page)
            image_data.update(data)
            image_data["page"] = i
            yield Message.Url, image_url, image_data
            if next_url:
                page = self.request(next_url).text

    def get_job_metadata(self, chapter_page):
        """Collect metadata for extractor-job"""
        page = self.request(self.url_base + self.url_title).text
        data = {
            "chapter": self.chapter,
            "lang": "en",
            "language": "English",
        }
        data, _ = text.extract_all(page, (
            (None, '<td class="propertytitle">Name:', ''),
            ("manga", '<h2 class="aname">', '</h2>'),
            (None, '<td class="propertytitle">Year of Release:', ''),
            ('manga-release', '<td>', '</td>'),
            (None, '<td class="propertytitle">Author:', ''),
            ('author', '<td>', '</td>'),
            (None, '<td class="propertytitle">Artist:', ''),
            ('artist', '<td>', '</td>'),
            (None, '<div id="readmangasum">', ''),
            ('title', ' ' + self.chapter + '</a> : ', '</td>'),
            ('chapter-date', '<td>', '</td>'),
        ), values=data)
        data, _ = text.extract_all(chapter_page, (
            (None, '<select id="pageMenu"', ''),
            ('count', '</select> of ', '</div>'),
        ), values=data)
        for key in ("author", "artist"):
            data[key] = text.unescape(data[key])
        data["manga"] = data["manga"].strip()
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
        return self.url_base + url, image, text.nameext_from_url(image, {
            "width": width,
            "height": height,
        })
