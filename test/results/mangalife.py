# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangasee
import datetime


__tests__ = (
{
    "#url"     : "https://manga4life.com/read-online/One-Piece-chapter-1063-page-1.html",
    "#category": ("", "mangalife", "chapter"),
    "#class"   : mangasee.MangaseeChapterExtractor,
    "#pattern" : r"https://[^/]+/manga/One-Piece/1063-0\d\d\.png",
    "#count"   : 13,

    "author"        : ["ODA Eiichiro"],
    "chapter"       : 1063,
    "chapter_minor" : "",
    "chapter_string": "110630",
    "count"         : 13,
    "date"          : "dt:2024-03-29 15:07:00",
    "extension"     : "png",
    "filename"      : r"re:1063-0\d\d",
    "genre"         : [
        "Action",
        "Adventure",
        "Comedy",
        "Drama",
        "Fantasy",
        "Shounen",
    ],
    "index"         : "1",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "One Piece",
    "page"          : int,
    "title"         : "",
},

{
    "#url"     : "https://manga4life.com/manga/Ano-Musume-Ni-Kiss-To-Shirayuri-O",
    "#category": ("", "mangalife", "manga"),
    "#class"   : mangasee.MangaseeMangaExtractor,
    "#pattern" : mangasee.MangaseeChapterExtractor.pattern,
    "#count"   : ">= 50",

    "author"        : ["Canno"],
    "chapter"       : int,
    "chapter_minor" : r"re:^|\.5$",
    "chapter_string": r"re:100\d\d\d",
    "date"          : datetime.datetime,
    "genre"         : [
        "Comedy",
        "Romance",
        "School Life",
        "Seinen",
        "Shoujo Ai",
    ],
    "index"         : "1",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "Ano-Musume-Ni-Kiss-To-Shirayuri-O",
    "title"         : "",
},

)
