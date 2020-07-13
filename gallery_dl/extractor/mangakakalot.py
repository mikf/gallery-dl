# -*- coding: utf-8 -*-

# Copyright 2020 Jake Mannens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangakakalot.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text


class MangakakalotBase():
    """Base class for mangakakalot extractors"""
    category = "mangakakalot"
    root = "https://mangakakalot.com"

    @staticmethod
    def parse_page(page, data):
        """Parse metadata on 'page' and add it to 'data'"""
        text.extract_all(page, (
            ("manga"  , '<h1>', '</h1>'),
            ('author' , '<li>Author(s) :\n', '</a>'),
        ), values=data)
        data["author"] = text.remove_html(data["author"])
        return data


class MangakakalotChapterExtractor(MangakakalotBase, ChapterExtractor):
    """Extractor for manga-chapters from mangakakalot.com"""
    archive_fmt = "{manga}_{chapter}_{page}"
    pattern = r"(?:https?://)?mangakakalot\.com(/chapter/([a-z]+\d+)/chapter_([0-9.]+))"

    def __init__(self, match):
        self.path, self.url_title, self.chapter = match.groups()
        ChapterExtractor.__init__(self, match, self.root + self.path)
        self.session.headers['Referer'] = self.root

    def metadata(self, chapter_page):
        page = self.request(self.root + "/manga/" + self.url_title).text
        churl = self.root + self.path
        chpage = self.request(churl).text
        chapter, sep, minor = self.chapter.partition(".")
        data = self.parse_page(page, {
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "lang": "en",
            "language": "English",
        })
        pos = page.index('href="' + churl + '"')
        data["title"] , pos = text.extract(page, '>', '<', pos)
        x = chpage.index('\n', chpage.index('<img', chpage.index('<div class="vung-doc"')))
        y = chpage.rfind('<img', 0, x)
        data["count"] = text.parse_int(text.extract(chpage[y:x], 'page ', ' - Mangakakalot.com"')[0])
        data["date"] , pos = text.extract(page, 'title="', '">', pos)
        return data

    def images(self, page):
        x = page.index('<div class="vung-doc"')
        y = page.index('\n', page.index('\n', x) + 1)
        page = page[x:y]
        pos = 0
        while True:
            image_url, pos = text.extract(page, 'src="', '"', pos)
            if not image_url:
                return
            if image_url.startswith('/ads/'):
                continue
            yield image_url, {}


class MangakakalotMangaExtractor(MangakakalotBase, MangaExtractor):
    """Extractor for manga from mangakakalot.com"""
    chapterclass = MangakakalotChapterExtractor
    reverse = False
    pattern = r"(?:https?://)?mangakakalot\.com(/manga/([a-z]+\d+))"

    def chapters(self, page):
        results = []
        data = self.parse_page(page, {"lang": "en", "language": "English"})

        needle = '<div class="row">\n<span><a href="'
        pos = page.index('<div class="chapter-list">')
        while True:
            url, pos = text.extract(page, needle, '"', pos)
            if not url:
                return results
            data["title"], pos = text.extract(page, '>', '</a>', pos)
            data["date"] , pos = text.extract(page, '<span title="', '">', pos)
            chapter, sep, minor = url.rpartition("/chapter_")[2].partition(".")
            data["chapter"] = text.parse_int(chapter)
            data["chapter_minor"] = sep + minor
            results.append((url, data.copy()))
