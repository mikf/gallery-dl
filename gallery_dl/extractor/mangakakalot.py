# -*- coding: utf-8 -*-

# Copyright 2020 Jake Mannens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangakakalot.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re


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
    pattern = (r"(?:https?://)?(?:www\.)?mangakakalot\.com"
               r"(/chapter/\w+/chapter_[^/?&#]+)")
    test = (
        ("https://mangakakalot.com/chapter/rx922077/chapter_6", {
            "pattern": r"https://s\d+\.\w+\.com/mangakakalot/r\d+/rx922077/"
                       r"chapter_6_master_help_me_out/\d+\.jpg",
            "keyword": "80fde46d2210a6c17f0b2f7c1c89f0f56b65e157",
            "count": 14,
        }),
        (("https://mangakakalot.com/chapter"
          "/hatarakanai_futari_the_jobless_siblings/chapter_20.1"), {
            "keyword": "6b24349bb16f41ef1c4350200c1ccda5f09ae136",
            "content": "7196aed8bb1536806bf55033ed1f2ed172c86f9a",
            "count": 2,
        }),
    )

    def __init__(self, match):
        self.path = match.group(1)
        ChapterExtractor.__init__(self, match, self.root + self.path)
        self.session.headers['Referer'] = self.root

    def metadata(self, page):
        _     , pos = text.extract(page, '<span itemprop="name">', '<')
        manga , pos = text.extract(page, '<span itemprop="name">', '<', pos)
        info  , pos = text.extract(page, '<span itemprop="name">', '<', pos)
        author, pos = text.extract(page, '. Author: ', ' already has ', pos)

        match = re.match(
            r"(?:[Vv]ol\. *(\d+) )?"
            r"[Cc]hapter *([^:]*)"
            r"(?:: *(.+))?", info)
        volume, chapter, title = match.groups() if match else ("", "", info)
        chapter, sep, minor = chapter.partition(".")

        return {
            "manga"        : text.unescape(manga),
            "title"        : text.unescape(title) if title else "",
            "author"       : text.unescape(author) if author else "",
            "volume"       : text.parse_int(volume),
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "lang"         : "en",
            "language"     : "English",
        }

    def images(self, page):
        page = text.extract(page, 'id="vungdoc"', '\n</div>')[0]
        return [
            (url, None)
            for url in text.extract_iter(page, '<img src="', '"')
        ]


class MangakakalotMangaExtractor(MangakakalotBase, MangaExtractor):
    """Extractor for manga from mangakakalot.com"""
    chapterclass = MangakakalotChapterExtractor
    pattern = (r"(?:https?://)?(?:www\.)?mangakakalot\.com"
               r"(/(?:manga/|read-)\w+)")
    test = (
        ("https://mangakakalot.com/manga/lk921810", {
            "url": "d262134b65993b031406f7b9d9442c9afd321a27",
        }),
        ("https://mangakakalot.com/read-ry3sw158504884246", {
            "pattern": MangakakalotChapterExtractor.pattern,
            "count": ">= 40"
        }),
    )

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
