# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangalib


__tests__ = (
{
    "#url"     : "https://mangalib.me/ru/189019--kimi-ni-koisuru-sanshimai/read/v1/c1",
    "#category": ("", "mangalib", "chapter"),
    "#class"   : mangalib.MangalibChapterExtractor,
    "#pattern" : r"https://img\d\.mixlib\.me//manga/[^/]+/chapters/\d+/[A-Za-z0-9._-]+\.(?:jpe?g|png|webp|avif)",

    "manga"        : str,
    "manga_slug"   : str,
    "volume"       : int,
    "chapter"      : int,
    "chapter_minor": str,
    "title"        : str,
    "lang"         : "ru",
    "language"     : "Russian",
    "page"         : int,
},

{
    "#url"     : "https://mangalib.me/ru/manga/19825--nichijou",
    "#category": ("", "mangalib", "manga"),
    "#class"   : mangalib.MangalibMangaExtractor,
    "#pattern" : mangalib.MangalibChapterExtractor.pattern,

    "manga"    : "nichijou",
    "manga_slug": "19825--nichijou",
    "volume"   : int,
    "chapter"  : int,
    "title"    : str,
    "lang"     : "ru",
    "language" : "Russian",
},
)
