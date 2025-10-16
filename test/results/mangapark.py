# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangapark


__tests__ = (
{
    "#url"     : "https://mangapark.net/title/114972-aria/6710214-en-ch.60.2",
    "#category": ("", "mangapark", "chapter"),
    "#class"   : mangapark.MangaparkChapterExtractor,
    "#pattern" : r"https://[\w-]+\.mp\w+\.org/media/2002/e67/61e29278a583b9227964076e/\d+_\d+_\d+_\d+\.jpeg",
    "#count"   : 70,

    "artist"       : ["amano kozue"],
    "author"       : ["amano kozue"],
    "chapter"      : 60,
    "chapter_id"   : 6710214,
    "chapter_minor": ".2",
    "count"        : 70,
    "date"         : "dt:2022-01-15 09:25:03",
    "extension"    : "jpeg",
    "filename"     : str,
    "genre"        : [
        "adventure",
        "comedy",
        "drama",
        "shounen",
        "slice_of_life",
    ],
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Aria",
    "manga_id"     : 114972,
    "page"         : int,
    "source"       : "Koala",
    "title"        : "Special Navigation - Aquaria Ii",
    "volume"       : 12,
},

{
    "#url"     : "https://mangapark.net/comic/10426/aria/c60.2-en-i6712231",
    "#comment" : "v3 URL",
    "#class"   : mangapark.MangaparkChapterExtractor,
    "#pattern" : r"https://[\w-]+\.mp\w+\.org/media/2001/a2e/61e2acf8062ec26ee5ef8e2a/\d+_\d+_\d+_\d+\.jpeg",
    "#count"   : 70,

    "chapter_id": 6712231,
},

{
    "#url"     : "https://mangapark.com/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://mangapark.org/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://mangapark.me/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://mangapark.io/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://mangapark.to/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://comicpark.org/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://comicpark.to/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://readpark.org/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://readpark.net/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://parkmanga.com/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://parkmanga.net/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://parkmanga.org/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},
{
    "#url"     : "https://mpark.to/title/114972-aria/6710214-en-ch.60.2",
    "#class"   : mangapark.MangaparkChapterExtractor,
},

{
    "#url"     : "https://mangapark.net/title/114972-aria",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
    "#pattern" : mangapark.MangaparkChapterExtractor.pattern,
    "#count"   : 71,

    "chapter"      : int,
    "chapter_id"   : r"re:\d+",
    "chapter_minor": str,
    "date"         : "type:datetime",
    "lang"         : "en",
    "language"     : "English",
    "manga_id"     : 114972,
    "source"       : "Horse",
    "source_id"    : "844",
    "title"        : str,
    "volume"       : int,
},

{
    "#url"     : "https://mangapark.net/comic/10426/aria",
    "#comment" : "v3 URL",
    "#class"   : mangapark.MangaparkMangaExtractor,
    "#pattern" : mangapark.MangaparkChapterExtractor.pattern,
    "#count"   : 74,

    "manga_id" : 10426,
},

{
    "#url"     : "https://mangapark.net/title/10504-en-mushishi",
    "#comment" : "'source' option",
    "#skip"    : "not functional",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
    "#pattern" : mangapark.MangaparkChapterExtractor.pattern,
    "#options" : {"source": "panda"},
    "#count"   : 70,

    "source"   : "Panda",
    "source_id": 15150116,
},

{
    "#url"     : "https://mangapark.com/title/114972-",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
},

{
    "#url"     : "https://mangapark.com/title/114972",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
},

{
    "#url"     : "https://mangapark.com/title/114972-aria",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
},

{
    "#url"     : "https://mangapark.org/title/114972-aria",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
},

{
    "#url"     : "https://mangapark.io/title/114972-aria",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
},

{
    "#url"     : "https://mangapark.me/title/114972-aria",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
},

)
