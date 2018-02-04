# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://subapics.com/"""

from . import komikcast
from .. import text


class SubapicsBase(komikcast.KomikcastBase):
    """Base class for subapics extractors"""
    category = "subapics"
    root = "https://subapics.com"


class SubapicsChapterExtractor(SubapicsBase,
                               komikcast.KomikcastChapterExtractor):
    """Extractor for manga-chapters from subapics.com"""
    pattern = [r"(?:https?://)?(?:www\.)?subapics\.com"
               r"(/[^/?&#]+-chapter-[^/?&#]+/?)$"]
    test = [("http://subapics.com/apotheosis-chapter-02-2/", {
        "url": "978d3c053d34a77f6ea6e60cbba3deda1e369be8",
        "keyword": "ed64479aef5a68aafa39334515f34a4595858c3c",
    })]

    @staticmethod
    def get_images(page):
        readerarea = text.extract(
            page, '<div id="readerarea">', '<meta/>')[0]
        return [
            (url, None)
            for url in text.extract_iter(
                readerarea, ' src="', '"'
            )
        ]


class SubapicsMangaExtractor(SubapicsBase,
                             komikcast.KomikcastMangaExtractor):
    """Extractor for manga from subapics.com"""
    pattern = [r"(?:https?://)?(?:www\.)?(subapics\.com/manga/[^/?&#]+/?)$"]
    test = [(("https://subapics.com/manga/"
              "rune-factory-4-koushiki-comic-visual-book/"), {
        "url": "6b18ba9513a6c92a23df1b78b11a1ad0013c6e5e",
        "keyword": "2fffe06b93b7ac8c4bb61f44398326deaf59fcf9",
    })]

    @staticmethod
    def get_metadata(page):
        manga , pos = text.extract(page, "<title>", "</title>")
        author, pos = text.extract(page, "<b>Author</b>: ", "</li>", pos)
        genres, pos = text.extract(page, "<b>Genres</b>: ", "</li>", pos)

        return {
            "manga": text.unescape(manga.rpartition(" – ")[0]),
            "author": text.unescape(author),
            "genres": text.remove_html(genres).replace(" , ", ", "),
        }
