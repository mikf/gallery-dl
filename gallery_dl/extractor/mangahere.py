# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://www.mangahere.co/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache
import re


class MangahereBase():
    """Base class for mangahere extractors"""
    category = "mangahere"
    root = "http://www.mangahere.cc"
    url_fmt = root + "/manga/{}/{}.html"


class MangahereMangaExtractor(MangahereBase, MangaExtractor):
    """Extractor for manga from mangahere.cc"""
    pattern = [r"(?:https?://)?(?:www\.|m\.)?mangahere\.c[co]/manga/"
               r"([^/]+)/?(?:#.*)?$"]
    test = [
        ("https://www.mangahere.cc/manga/aria/", {
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
        url = "{}/manga/{}/".format(self.root, match.group(1))
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
            results.append((text.urljoin("http:", url), {
                "manga": manga, "title": title, "date": date,
                "volume": text.parse_int(volume.rpartition(" ")[2]),
                "chapter": text.parse_int(chapter),
                "chapter_minor": dot + minor,
                "lang": "en", "language": "English",
            }))


class MangahereChapterExtractor(MangahereBase, ChapterExtractor):
    """Extractor for manga-chapters from mangahere.cc"""
    pattern = [(r"(?:https?://)?(?:www\.|m\.)?mangahere\.c[co]/manga/"
                r"([^/]+(?:/v0*(\d+))?/c([^/?&#]+))")]
    test = [
        ("https://www.mangahere.cc/manga/dongguo_xiaojie/c004.2/", {
            "keyword": "0e1cee6dd377da02ad51aa810ba65db3e811aef9",
            "content": "708d475f06893b88549cbd30df1e3f9428f2c884",
        }),
        ("http://www.mangahere.co/manga/dongguo_xiaojie/c003.2/", None),
        ("http://m.mangahere.co/manga/dongguo_xiaojie/c003.2/", None),
    ]

    def __init__(self, match):
        self.part, self.volume, self.chapter = match.groups()
        # remove ".html" for the first chapter page to avoid redirects
        url = self.url_fmt.format(self.part, "")[:-5]
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        manga, pos = text.extract(page, '<title>', '</title>')
        mid  , pos = text.extract(page, '.net/store/manga/', '/', pos)
        pages, pos = text.extract(page, ' class="wid60"', '</select>', pos)
        count = re.findall(r">(\d+)<", pages)[-1]
        manga = re.match((r"(.+) \d+(\.\d+)? - Read .+ Chapter "
                          r"\d+(\.\d+)? Online"), manga).group(1)
        chapter, dot, minor = self.chapter.partition(".")

        return {
            "manga": text.unescape(manga),
            "manga_id": text.parse_int(mid),
            "title": self._get_title_map(mid).get(self.chapter),
            "volume": text.parse_int(self.volume),
            "chapter": text.parse_int(chapter),
            "chapter_minor": dot + minor,
            "count": text.parse_int(count),
            "lang": "en",
            "language": "English",
        }

    def get_images(self, page):
        """Yield all image-urls for this chapter"""
        pnum = 1
        while True:
            for url in text.extract_iter(page, '<img src="', '"'):
                if "/store/manga/" in url:
                    yield url, None
            pnum += 2
            page = self.request(self.url_fmt.format(self.part, pnum)).text

    @memcache(keyarg=1)
    def _get_title_map(self, manga_id):
        url = "{}/get_chapters{}.js".format(self.root, manga_id)
        page = self.request(url).text

        chapters = {}
        for info in text.extract_iter(page, '["', '"]'):
            title, _, url = info.partition('","')
            title = title.partition(": ")[2]
            num = url.rpartition("c")[2].rstrip("/")
            chapters[num] = text.unescape(title)

        return chapters
