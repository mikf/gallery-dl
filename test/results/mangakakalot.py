# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangakakalot


__tests__ = (
{
    "#url"     : "https://ww3.mangakakalot.tv/chapter/manga-jk986845/chapter-34.2",
    "#category": ("", "mangakakalot", "chapter"),
    "#class"   : mangakakalot.MangakakalotChapterExtractor,
    "#pattern"      : r"https://cm\.blazefast\.co/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.jpg",
    "#count"        : 9,
    "#sha1_metadata": "0f1586ff52f0f9cbbb25306ae64ab718f8a6a633",
},

{
    "#url"     : "https://mangakakalot.tv/chapter/hatarakanai_futari_the_jobless_siblings/chapter_20.1",
    "#category": ("", "mangakakalot", "chapter"),
    "#class"   : mangakakalot.MangakakalotChapterExtractor,
},

{
    "#url"     : "https://ww3.mangakakalot.tv/manga/manga-jk986845",
    "#category": ("", "mangakakalot", "manga"),
    "#class"   : mangakakalot.MangakakalotMangaExtractor,
    "#pattern" : mangakakalot.MangakakalotChapterExtractor.pattern,
    "#count"   : ">= 30",
},

{
    "#url"     : "https://mangakakalot.tv/manga/lk921810",
    "#category": ("", "mangakakalot", "manga"),
    "#class"   : mangakakalot.MangakakalotMangaExtractor,
},

)
