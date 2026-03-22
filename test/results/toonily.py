# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import toonily


__tests__ = (
{
    "#url"     : "https://toonily.com/page/2/",
    "#category": ("wpmadara", "toonily", "home"),
    "#class"   : toonily.ToonilyHomeExtractor,
    "#pattern" : toonily.ToonilyMangaExtractor.pattern,
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : "https://toonily.com/tag/harem/",
    "#category": ("wpmadara", "toonily", "tag"),
    "#class"   : toonily.ToonilyTagExtractor,
    "#pattern" : toonily.ToonilyMangaExtractor.pattern,
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : "https://toonily.com/genre/historical/",
    "#category": ("wpmadara", "toonily", "genre"),
    "#class"   : toonily.ToonilyGenreExtractor,
    "#pattern" : toonily.ToonilyMangaExtractor.pattern,
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : "https://toonily.com/serie/bj-archmage/chapter-1/",
    "#category": ("wpmadara", "toonily", "chapter"),
    "#class"   : toonily.ToonilyChapterExtractor,
    "#pattern" : r"https://data\.tnlycdn\.com/chapters/manga_69a777df554f1/"
                 r"bdbb2b75b74c3b06fa2f3e15cc8477d9/BJ-Archmage_\d{2}\.jpg",
    "#count"   : 10,

    "artist"       : ["SADO"],
    "author"       : ["D-Dart"],
    "chapter"      : 1,
    "chapter_minor": "",
    "count"        : 10,
    "description"  : r"re:.*After getting electrocuted, he begins to see "
                     r"things that shouldn't be seen in-game\.",
    "extension"    : "jpg",
    "genres"       : [
        "Action",
        "Adventure",
        "Fantasy",
        "Shounen",
    ],
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "BJ Archmage",
    "manga_alt"    : ["대마도사"],
    "page"         : range(1, 10),
    "rating"       : 0.0,
    "status"       : "Completed",
    "title"        : "",
},

{
    "#url"     : "https://toonily.com/serie/bj-archmage/chapter-52-5/",
    "#category": ("wpmadara", "toonily", "chapter"),
    "#class"   : toonily.ToonilyChapterExtractor,
},

{
    "#url"     : "https://toonily.com/serie/bj-archmage/",
    "#category": ("wpmadara", "toonily", "manga"),
    "#class"   : toonily.ToonilyMangaExtractor,
    "#pattern" : toonily.ToonilyChapterExtractor.pattern,
    "#count"   : 145,

    "artist"       : ["SADO"],
    "author"       : ["D-Dart"],
    "chapter"      : range(1, 145),
    "chapter_minor": {"", ".5"},
    "description"  : r"re:.*After getting electrocuted, he begins to see "
                     r"things that shouldn't be seen in-game\.",
    "genres"       : [
        "Action",
        "Adventure",
        "Fantasy",
        "Shounen",
    ],
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "BJ Archmage",
    "manga_alt"    : ["대마도사"],
    "rating"       : 0.0,
    "status"       : "Completed",
    "title"        : {
        "",
        "The End",
        "Season 3",
        "Season 2 Finale",
        "Season 1 Finale",
    },
},

{
    "#url"     : "https://toonily.com/serie/bj-archmage",
    "#category": ("wpmadara", "toonily", "manga"),
    "#class"   : toonily.ToonilyMangaExtractor,
},

{
    "#url"     : "https://toonily.com/",
    "#category": ("wpmadara", "toonily", "home"),
    "#class"   : toonily.ToonilyHomeExtractor,
},

)
