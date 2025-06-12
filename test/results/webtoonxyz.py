# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wpmadara
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.webtoon.xyz/read/the-world-after-the-end/chapter-105/",
    "#category": ("wpmadara", "webtoonxyz", "chapter"),
    "#class"   : wpmadara.WPMadaraChapterExtractor,
    "#pattern" : r"https://www\.webtoon\.xyz/wp-content/uploads/WP-manga/data/manga_[^/]+/[^/]+/[^.]+\.\w+",
    "#count"   : 11,

    "manga"        : "The World After The End",
    "title"        : "",
    "chapter"      : 105,
    "lang"         : "en",
    "language"     : "English",
},

{
    "#url"     : "https://www.webtoon.xyz/read/the-world-after-the-end/chapter-1000000/",
    "#category": ("wpmadara", "webtoonxyz", "chapter"),
    "#class"   : wpmadara.WPMadaraChapterExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.webtoon.xyz/read/the-world-after-the-end/",
    "#category": ("wpmadara", "webtoonxyz", "manga"),
    "#class"   : wpmadara.WPMadaraMangaExtractor,
    "#pattern" : r"https://www\.webtoon\.xyz/read/such-a-cute-spy/chapter-\d+([_-].+)?/",
    "#count"   : ">= 13",

    "manga"      : "The World After The End",
    "author"     : ["S-Cynaan", "Sing Shong"],
    "artist"     : ["Undead Potato"],
    "genres"     : [
        "Action",
        "Adventure",
        "Fantasy",
    ],
    "rating"     : float,
    "status"     : "OnGoing",
    "lang"       : "en",
    "language"   : "English",
    "manga_alt"  : list,
},

{
    "#url"     : "https://www.webtoon.xyz/read/doesnotexist",
    "#category": ("wpmadara", "webtoonxyz", "manga"),
    "#class"   : wpmadara.WPMadaraMangaExtractor,
    "#exception": exception.HttpError,
},

)
