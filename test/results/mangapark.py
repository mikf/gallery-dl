# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangapark
import datetime


__tests__ = (
{
    "#url"     : "https://mangapark.net/title/114972-aria/6710214-en-ch.60.2",
    "#category": ("", "mangapark", "chapter"),
    "#class"   : mangapark.MangaparkChapterExtractor,
    "#pattern" : r"https://[\w-]+\.mpcdn\.org/comic/2002/e67/61e29278a583b9227964076e/\d+_\d+_\d+_\d+\.jpeg\?acc=[^&#]+&exp=\d+",
    "#count"   : 70,

    "artist"       : [],
    "author"       : ["Amano Kozue"],
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
        "sci_fi",
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
    "#url"     : "https://mangapark.com/title/114972-aria/6710214-en-ch.60.2",
    "#category": ("", "mangapark", "chapter"),
    "#class"   : mangapark.MangaparkChapterExtractor,
},

{
    "#url"     : "https://mangapark.org/title/114972-aria/6710214-en-ch.60.2",
    "#category": ("", "mangapark", "chapter"),
    "#class"   : mangapark.MangaparkChapterExtractor,
},

{
    "#url"     : "https://mangapark.io/title/114972-aria/6710214-en-ch.60.2",
    "#category": ("", "mangapark", "chapter"),
    "#class"   : mangapark.MangaparkChapterExtractor,
},

{
    "#url"     : "https://mangapark.me/title/114972-aria/6710214-en-ch.60.2",
    "#category": ("", "mangapark", "chapter"),
    "#class"   : mangapark.MangaparkChapterExtractor,
},

{
    "#url"     : "https://mangapark.net/title/114972-aria",
    "#comment" : "'source' option",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
    "#pattern" : mangapark.MangaparkChapterExtractor.pattern,
    "#count"   : 141,

    "chapter"      : int,
    "chapter_id"   : int,
    "chapter_minor": str,
    "date"         : datetime.datetime,
    "lang"         : "en",
    "language"     : "English",
    "manga_id"     : 114972,
    "source"       : r"re:Horse|Koala",
    "source_id"    : int,
    "title"        : str,
    "volume"       : int,
},

{
    "#url"     : "https://mangapark.net/title/114972-aria",
    "#comment" : "'source' option",
    "#category": ("", "mangapark", "manga"),
    "#class"   : mangapark.MangaparkMangaExtractor,
    "#options" : {"source": "koala"},
    "#pattern" : mangapark.MangaparkChapterExtractor.pattern,
    "#count"   : 70,

    "source"   : "Koala",
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
