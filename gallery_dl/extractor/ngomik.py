# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
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
    pattern = (r"(?:https?://)?(?:www\.)?ngomik\.in"
               r"/([^/?&#]+-chapter-[^/?&#]+)")
    test = ("https://www.ngomik.in/14-sai-no-koi-chapter-1-6/", {
        "url": "8e67fdf751bbc79bc6f4dead7675008ddb8e32a4",
        "keyword": "7cc913ed2b9018afbd3336755d28b8252d83044c",
    })

    def __init__(self, match):
        url = "{}/{}".format(self.root, match.group(1))
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        info = text.extract(page, '<title>', "</title>")[0]
        manga, _, chapter = info.partition(" Chapter ")
        chapter, sep, minor = chapter.partition(" ")[0].partition(".")

        return {
            "manga": text.unescape(manga),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "lang": "id",
            "language": "Indonesian",
        }

    @staticmethod
    def get_images(page):
        readerarea = text.extract(page, 'id="readerarea"', 'class="chnav"')[0]
        return [
            (text.unescape(url), None)
            for url in text.extract_iter(readerarea, ' src="', '"')
        ]
