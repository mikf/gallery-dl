# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://ngomik.in/"""

from .common import ChapterExtractor
from .. import text


class NgomikChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from ngomik.in"""
    category = "ngomik"
    root = "http://ngomik.in"
    pattern = [r"(?:https?://)?(?:www\.)?ngomik\.in"
               r"/manga/([^/?&#]+/chapter-[^/?&#]+)"]
    test = [(("http://ngomik.in/manga/chuuko-demo-koi-ga-shitai"
              "/chapter-21-5?style=list"), {
        "url": "e87ed713f31d576013f179b50b4e10d7c678e53a",
        "keyword": "a774caea148fc18a7d889f453dadbe3def9e0c2c",
    })]

    def __init__(self, match):
        url = "{}/manga/{}?style=list".format(self.root, match.group(1))
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        info = text.extract(page, '<title>', "</title>")[0]
        manga, chapter, _ = info.split(" - ")
        chapter, sep, minor = chapter.rpartition(" ")[2].partition(".")

        return {
            "manga": text.unescape(manga),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "lang": "id",
            "language": "Indonesian",
        }

    @staticmethod
    def get_images(page):
        readerarea = text.extract(
            page, '<div class="page-break', '<div class="select-view')[0]
        return [
            (url, None)
            for url in text.extract_iter(
                readerarea, ' src="', '"'
            )
        ]
