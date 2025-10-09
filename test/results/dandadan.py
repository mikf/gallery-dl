# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import dandadan


__tests__ = (
{
    "#url"     : "https://dandadan.net/manga/dandadan-chapter-1/",
    "#class"   : dandadan.DandadanChapterExtractor,
    "#pattern" : r"https://cdn\.readkakegurui\.com/file/cdnpog/dandadan/chapter\-1/\d+\.webp",
    "#count"   : 67,

    "chapter"  : 1,
    "count"    : 67,
    "page"     : range(1, 67),
    "extension": "webp",
    "lang"     : "en",
    "manga"    : "Dandadan",
},

{
    "#url"     : "https://dandadan.net/manga/dandadan-chapter-40-5-3/",
    "#class"   : dandadan.DandadanChapterExtractor,
    "#pattern" : r"https://cdn\.readkakegurui\.com/file/cdnpog/dandadan/chapter\-40\.5/\d+\.webp",
    "#count"   : 35,

    "chapter"      : 40,
    "chapter_minor": ".5",
},

{
    "#url"     : "https://dandadan.net/manga/dandadan-chapter-203/",
    "#class"   : dandadan.DandadanChapterExtractor,
    "#pattern" : r"https://pic\.readkakegurui\.com/file/sancdn/dandadan/chapter\-203/\d+\.webp",
    "#count"   : 22,

    "chapter": 203,
},

{
    "#url"     : "https://dandadan.net/",
    "#class"   : dandadan.DandadanMangaExtractor,
    "#pattern" : dandadan.DandadanChapterExtractor.pattern,
    "#count"   : range(210, 300),
},

)
