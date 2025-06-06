# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangaread
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.mangaread.org/manga/one-piece/chapter-1053-3/",
    "#category": ("", "mangaread", "chapter"),
    "#class"   : mangaread.MangareadChapterExtractor,
    "#pattern" : r"https://www\.mangaread\.org/wp-content/uploads/WP-manga/data/manga_[^/]+/[^/]+/[^.]+\.\w+",
    "#count"   : 11,

    "manga"        : "One Piece",
    "title"        : "",
    "chapter"      : 1053,
    "chapter_minor": ".3",
    "tags"         : ["Oda Eiichiro"],
    "lang"         : "en",
    "language"     : "English",
},

{
    "#url"     : "https://www.mangaread.org/manga/one-piece/chapter-1000000/",
    "#category": ("", "mangaread", "chapter"),
    "#class"   : mangaread.MangareadChapterExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.mangaread.org/manga/kanan-sama-wa-akumade-choroi/chapter-10/",
    "#category": ("", "mangaread", "chapter"),
    "#class"   : mangaread.MangareadChapterExtractor,
    "#pattern" : r"https://www\.mangaread\.org/wp-content/uploads/WP-manga/data/manga_[^/]+/[^/]+/[^.]+\.\w+",
    "#count"   : 9,

    "manga"        : "Kanan-sama wa Akumade Choroi",
    "title"        : "",
    "chapter"      : 10,
    "chapter_minor": "",
    "tags"         : list,
    "lang"         : "en",
    "language"     : "English",
},

{
    "#url"     : "https://www.mangaread.org/manga/above-all-gods/chapter146-5/",
    "#comment" : "^^ no whitespace",
    "#category": ("", "mangaread", "chapter"),
    "#class"   : mangaread.MangareadChapterExtractor,
    "#pattern" : r"https://www\.mangaread\.org/wp-content/uploads/WP-manga/data/manga_[^/]+/[^/]+/[^.]+\.\w+",
    "#count"   : 6,

    "manga"        : "Above All Gods",
    "title"        : "",
    "chapter"      : 146,
    "chapter_minor": ".5",
    "tags"         : list,
    "lang"         : "en",
    "language"     : "English",
},

{
    "#url"     : "https://www.mangaread.org/manga/kanan-sama-wa-akumade-choroi",
    "#category": ("", "mangaread", "manga"),
    "#class"   : mangaread.MangareadMangaExtractor,
    "#pattern" : r"https://www\.mangaread\.org/manga/kanan-sama-wa-akumade-choroi/chapter-\d+([_-].+)?/",
    "#count"   : ">= 13",

    "manga"      : "Kanan-sama wa Akumade Choroi",
    "author"     : ["nonco"],
    "artist"     : ["nonco"],
    "type"       : "Manga",
    "genres"     : [
        "Comedy",
        "Romance",
        "Shounen",
        "Supernatural",
    ],
    "rating"     : float,
    "release"    : 2022,
    "status"     : "OnGoing",
    "lang"       : "en",
    "language"   : "English",
    "manga_alt"  : list,
    "description": str,
},

{
    "#url"     : "https://www.mangaread.org/manga/one-piece",
    "#category": ("", "mangaread", "manga"),
    "#class"   : mangaread.MangareadMangaExtractor,
    "#pattern" : r"https://www\.mangaread\.org/manga/one-piece/chapter-\d+(-.+)?/",
    "#count"   : ">= 1066",

    "manga"      : "One Piece",
    "author"     : ["Oda Eiichiro"],
    "artist"     : ["Oda Eiichiro"],
    "type"       : "Manga",
    "genres"     : list,
    "rating"     : float,
    "release"    : 1997,
    "status"     : "OnGoing",
    "lang"       : "en",
    "language"   : "English",
    "manga_alt"  : ["One Piece"],
    "description": str,
},

{
    "#url"     : "https://www.mangaread.org/manga/doesnotexist",
    "#category": ("", "mangaread", "manga"),
    "#class"   : mangaread.MangareadMangaExtractor,
    "#exception": exception.NotFoundError,
},

)
