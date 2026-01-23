# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import kaliscan


__tests__ = (
{
    "#url"     : "https://kaliscan.me/manga/2142-whats-wrong-with-secretary-kim/chapter-1",
    "#class"   : kaliscan.KaliscanChapterExtractor,
    "#pattern" : r"https://s\d+\.1stmggv\d*\.\w+/.+\.\w+",
    "#count"   : 13,

    "author"       : "Jeong gyeong yun",
    "chapter"      : 1,
    "chapter_minor": "",
    "chapter_id"   : 68134,
    "count"        : 13,
    "genres"       : ["Comedy", "Josei", "Manhwa", "Romance", "Webtoons"],
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "What's Wrong with Secretary Kim?",
    "manga_id"     : 2142,
    "manga_slug"   : "2142-whats-wrong-with-secretary-kim",
    "status"       : "Completed",
},

{
    "#url"     : "https://kaliscan.me/manga/2142-whats-wrong-with-secretary-kim/chapter-14.5",
    "#class"   : kaliscan.KaliscanChapterExtractor,

    "chapter"      : 14,
    "chapter_minor": ".5",
},

{
    "#url"     : "https://kaliscan.me/manga/2142-whats-wrong-with-secretary-kim",
    "#class"   : kaliscan.KaliscanMangaExtractor,
    "#pattern" : kaliscan.KaliscanChapterExtractor.pattern,
    "#count"   : range(100, 200),

    "author"   : "Jeong gyeong yun",
    "chapter"  : int,
    "genres"   : ["Comedy", "Josei", "Manhwa", "Romance", "Webtoons"],
    "lang"     : "en",
    "manga"    : "What's Wrong with Secretary Kim?",
    "manga_id" : 2142,
    "status"   : "Completed",
},

)
