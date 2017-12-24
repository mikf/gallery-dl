# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://jaiminisbox.com/"""

from . import foolslide


class JaiminisboxChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from jaiminisbox.com"""
    category = "jaiminisbox"
    pattern = foolslide.chapter_pattern(r"(?:www\.)?jaiminisbox\.com/reader")
    test = [
        ("https://jaiminisbox.com/reader/read/uratarou/en/0/1/", {
            "keyword": "d8919bc8f0351b44e938862214e654401962b5a5",
        }),
        ("https://jaiminisbox.com/reader/read/dr-stone/en/0/16/", {
            "keyword": "9b658599651f1ae87cab3e0e29dd21e8337a362c",
        }),
    ]
    method = "base64"


class JaiminisboxMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from jaiminisbox.com"""
    category = "jaiminisbox"
    pattern = foolslide.manga_pattern(r"(?:www\.)?jaiminisbox\.com/reader")
    test = [("https://jaiminisbox.com/reader/series/sora_no_kian/", {
        "url": "66612be177dc3b3fa1d1f537ef02f4f701b163ea",
        "keyword": "0908a4145bb03acc4210f5d01169988969f5acd1",
    })]
