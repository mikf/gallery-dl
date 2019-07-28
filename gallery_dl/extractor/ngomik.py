# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://ngomik.in/"""

from .common import ChapterExtractor
from .. import text
import re


class NgomikChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from ngomik.in"""
    category = "ngomik"
    root = "http://ngomik.in"
    pattern = (r"(?:https?://)?(?:www\.)?ngomik\.in"
               r"(/[^/?&#]+-chapter-[^/?&#]+)")
    test = (
        ("https://www.ngomik.in/14-sai-no-koi-chapter-1-6/", {
            "url": "8e67fdf751bbc79bc6f4dead7675008ddb8e32a4",
            "keyword": "204d177f09d438fd50c9c28d98c73289194640d8",
        }),
        ("https://ngomik.in/break-blade-chapter-26/", {
            "count": 34,
        }),
    )

    def metadata(self, page):
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
    def images(page):
        readerarea = text.extract(page, 'id="readerarea"', 'class="chnav"')[0]
        return [
            (text.unescape(url), None)
            for url in re.findall(r"\ssrc=[\"']?([^\"' >]+)", readerarea)
        ]
