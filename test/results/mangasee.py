# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangasee
import datetime


__tests__ = (
{
    "#url"     : "https://mangasee123.com/read-online/Tokyo-Innocent-chapter-4.5-page-1.html",
    "#category": ("", "mangasee", "chapter"),
    "#class"   : mangasee.MangaseeChapterExtractor,
    "#pattern" : r"https://[^/]+/manga/Tokyo-Innocent/0004\.5-00\d\.png",
    "#count"   : 8,

    "author"        : ["NARUMI Naru"],
    "chapter"       : 4,
    "chapter_minor" : ".5",
    "chapter_string": "100045",
    "count"         : 8,
    "date"          : "dt:2020-01-20 21:52:53",
    "extension"     : "png",
    "filename"      : r"re:0004\.5-00\d",
    "genre"         : [
        "Comedy",
        "Fantasy",
        "Harem",
        "Romance",
        "Shounen",
        "Supernatural",
    ],
    "index"         : "1",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "Tokyo Innocent",
    "page"          : int,
    "title"         : "",
},

{
    "#url"     : "https://mangasee123.com/manga/Nakamura-Koedo-To-Daizu-Keisuke-Wa-Umaku-Ikanai",
    "#category": ("", "mangasee", "manga"),
    "#class"   : mangasee.MangaseeMangaExtractor,
    "#pattern" : mangasee.MangaseeChapterExtractor.pattern,
    "#count"   : ">= 17",

    "author"        : ["TAKASE Masaya"],
    "chapter"       : int,
    "chapter_minor" : r"re:^|\.5$",
    "chapter_string": r"re:100\d\d\d",
    "date"          : datetime.datetime,
    "genre"         : [
        "Comedy",
        "Romance",
        "School Life",
        "Shounen",
        "Slice of Life",
    ],
    "index"         : "1",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "Nakamura-Koedo-To-Daizu-Keisuke-Wa-Umaku-Ikanai",
    "title"         : "",
},

)
