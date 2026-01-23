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

{
    "#url"     : "https://mangalib.me/ru/manga/21950--ashita-no-joe",
    "#category": ("", "mangalib", "manga"),
    "#class"   : mangalib.MangalibMangaExtractor,
    "#pattern" : mangalib.MangalibChapterExtractor.pattern,
    "#count"   : 126,

    "manga"    : "ashita no joe",
    "manga_slug": "21950--ashita-no-joe",
    "volume"   : int,
    "chapter"  : range(1, 126),
    "chapter_minor": {"", ".5"},
    "title"    : str,
    "lang"     : "ru",
    "language" : "Russian",
},

{
    "#url"     : "https://mangalib.me/ru/21950--ashita-no-joe/read/v1/c5",
    "#category": ("", "mangalib", "chapter"),
    "#class"   : mangalib.MangalibChapterExtractor,
    "#count"   : 24,

    "manga"    : "ashita no joe",
    "manga_slug": "21950--ashita-no-joe",
    "volume"   : 1,
    "chapter"  : 5,
    "chapter_minor": "",
    "title"    : str,
    "lang"     : "ru",
    "language" : "Russian",
    "page"     : range(1, 25),
},

{
    "#url"     : "https://mangalib.me/ru/21950--ashita-no-joe/read/v8/c80.5",
    "#category": ("", "mangalib", "chapter"),
    "#class"   : mangalib.MangalibChapterExtractor,
    "#pattern" : r"https://img3\.mixlib\.me//manga/ashita-no-joe/chapters/2022662/[A-Za-z0-9._-]+\.png",
    "#count"   : 14,

    "manga"    : "ashita no joe",
    "manga_slug": "21950--ashita-no-joe",
    "volume"   : 8,
    "chapter"  : 80,
    "chapter_minor": ".5",
    "title"    : str,
    "lang"     : "ru",
    "language" : "Russian",
    "page"     : range(1, 15),
},

)
