# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangahere.co/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
from urllib.parse import urljoin
import re


class MangahereMangaExtractor(MangaExtractor):
    """Extractor for manga from mangahere.co"""
    category = "mangahere"
    pattern = [r"(?:https?://)?(?:www\.|m\.)?mangahere\.c[co]/manga/"
               r"([^/]+)/?(?:#.*)?$"]
    test = [
        ("http://www.mangahere.cc/manga/aria/", {
            "url": "e8971b1605d9888d978ebb2895adb1c7c37d663c",
            "keyword": "951eef36a3775525a31ca78c9d9cea546f4cf2f5",
        }),
        ("http://www.mangahere.cc/manga/hiyokoi#50", {
            "url": "6df27c0e105d9ee0b78a7aa77340d0891e6c7fc6",
            "keyword": "9542283639bd082fabf3a14b6695697d3ef15111",
        }),
        ("http://www.mangahere.co/manga/aria/", None),
        ("http://m.mangahere.co/manga/aria/", None),
    ]

    def __init__(self, match):
        url = "http://www.mangahere.cc/manga/" + match.group(1) + "/"
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        results = []
        pos = page.index('<div class="detail_list">')
        manga, pos = text.extract(page, '<h3>Read ', ' Online</h3>', pos)
        manga = text.unescape(manga)

        while True:
            url, pos = text.extract(
                page, '<a class="color_0077" href="', '"', pos)
            if not url:
                return results
            chapter, dot, minor = url[:-1].rpartition("/c")[2].partition(".")
            volume, pos = text.extract(page, 'span class="mr6">', '<', pos)
            title, pos = text.extract(page, '/span>', '<', pos)
            date, pos = text.extract(page, 'class="right">', '</span>', pos)
            results.append((urljoin("http:", url), {
                "manga": manga, "title": title, "date": date,
                "volume": util.safe_int(volume.rpartition(" ")[2]),
                "chapter": util.safe_int(chapter),
                "chapter_minor": dot + minor,
                "lang": "en", "language": "English",
            }))


class MangahereChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from mangahere.co"""
    category = "mangahere"
    pattern = [(r"(?:https?://)?(?:www\.|m\.)?mangahere\.c[co]/manga/"
                r"([^/]+(?:/v0*(\d+))?/c0*(\d+)(\.\d+)?)")]
    test = [
        ("http://www.mangahere.cc/manga/dongguo_xiaojie/c003.2/", {
            "keyword": "0c263b83f803524baa8717d2b4d841617aa8d775",
            "content": "dd8454469429c6c717cbc3cad228e76ef8c6e420",
        }),
        ("http://www.mangahere.co/manga/dongguo_xiaojie/c003.2/", None),
        ("http://m.mangahere.co/manga/dongguo_xiaojie/c003.2/", None),
    ]
    url_fmt = "http://www.mangahere.cc/manga/{}/{}.html"

    def __init__(self, match):
        self.part, self.volume, self.chapter, self.chminor = match.groups()
        # remove ".html" for the first chapter page to avoid redirects
        url = self.url_fmt.format(self.part, "")[:-5]
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        manga, pos = text.extract(page, '<title>', '</title>')
        chid , pos = text.extract(page, '.net/store/manga/', '/', pos)
        pages, pos = text.extract(page, ' class="wid60"', '</select>', pos)
        count = re.findall(r">(\d+)<", pages)[-1]
        manga = re.match((r"(.+) \d+(\.\d+)? - Read .+ Chapter "
                          r"\d+(\.\d+)? Online"), manga).group(1)
        return {
            "manga": text.unescape(manga),
            # "title": TODO,
            "volume": util.safe_int(self.volume),
            "chapter": util.safe_int(self.chapter),
            "chapter_minor": self.chminor or "",
            "chapter_id": util.safe_int(chid),
            "count": util.safe_int(count),
            "lang": "en",
            "language": "English",
        }

    def get_images(self, page):
        """Yield all image-urls for this chapter"""
        pnum = 1
        while True:
            url, pos = text.extract(page, '<img src="', '"')
            yield url, None
            _  , pos = text.extract(page, '<img src="', '"', pos)
            _  , pos = text.extract(page, '<img src="', '"', pos)
            url, pos = text.extract(page, '<img src="', '"', pos)
            yield url, None

            pnum += 2
            page = self.request(self.url_fmt.format(self.part, pnum)).text
