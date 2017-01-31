# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangahere.co/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text
import re


class MangahereMangaExtractor(Extractor):
    """Extractor for mangas from mangahere.co"""
    category = "mangahere"
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?mangahere\.co/manga/([^/]+)/?$"]
    test = [("http://www.mangahere.co/manga/aria/", {
        "url": "77d96842292a6a341e8937816ed45cc09b538cf0",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0) + "/"

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request(self.url).text
        return reversed(list(text.extract_iter(
            page, '<a class="color_0077" href="', '"',
            page.index('<div class="detail_list">')
        )))


class MangahereChapterExtractor(AsynchronousExtractor):
    """Extractor for manga-chapters from mangahere.co"""
    category = "mangahere"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{chapter-minor}"]
    filename_fmt = ("{manga}_c{chapter:>03}{chapter-minor}_"
                    "{page:>03}.{extension}")
    pattern = [(r"(?:https?://)?(?:www\.)?mangahere\.co/manga/"
                r"([^/]+(?:/v0*(\d+))?/c0*(\d+)(\.\d+)?)")]
    test = [("http://www.mangahere.co/manga/dongguo_xiaojie/c003.2/", {
        "keyword": "d3fe470e934a9f02ed00d4391b1743970eae82fa",
        "content": "dd8454469429c6c717cbc3cad228e76ef8c6e420",
    })]
    url_fmt = "http://www.mangahere.co/manga/{}/{}.html"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.part, self.volume, self.chapter, self.chminor = match.groups()

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
        manga, pos = text.extract(page, '<title>', '</title>')
        chid , pos = text.extract(page, 'h.mhcdn.net/store/manga/', '/', pos)
        _    , pos = text.extract(page, '<select class="wid60"', '', pos)
        _    , pos = text.extract(page, '</select>', '', pos)
        count, pos = text.extract(page, '>', '<', pos-30)
        manga = re.match((r"(.+) \d+(\.\d+)? - Read .+ Chapter "
                          r"\d+(\.\d+)? Online"), manga).group(1)
        return {
            "manga": text.unescape(manga),
            # "title": TODO,
            "volume": self.volume or "",
            "chapter": self.chapter,
            "chapter-minor": self.chminor or "",
            "chapter-id": chid,
            "count": count,
            "lang": "en",
            "language": "English",
        }

    def get_image_urls(self, page):
        """Yield all image-urls for this chapter"""
        pnum = 1
        while True:
            url, pos = text.extract(page, '<img src="', '"')
            yield url
            _  , pos = text.extract(page, '<img src="', '"', pos)
            _  , pos = text.extract(page, '<img src="', '"', pos)
            url, pos = text.extract(page, '<img src="', '"', pos)
            yield url
            pnum += 2
            page = self.request(self.url_fmt.format(self.part, pnum)).text
