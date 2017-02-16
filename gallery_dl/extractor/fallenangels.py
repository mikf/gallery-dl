# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://famatg.com/"""

from . import foolslide


class FallenangelsChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from famatg.com"""
    category = "fallenangels"
    pattern = foolslide.chapter_pattern(r"(?:manga|truyen)\.famatg\.com")
    test = [
        ("http://manga.famatg.com/read/chronos_ruler/en/0/20/", {
            "url": "a777f93533674744b74c9b57c7dfa7254f5ddbed",
            "keyword": "76e7130a64d96317e3e4dcd55d770c9f6d9cb71d",
        }),
        ("https://truyen.famatg.com/read/madan_no_ou_to_vanadis/vi/0/33/", {
            "url": "b46bf1ef0537c3ce42bf2b9e4b62ace41c2299cd",
            "keyword": "658cdbecd3a1698f5462c1db437b423b6bcf7dd3",
        }),
    ]
