# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wpmadara
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://toonily.com/webtoon/such-a-cute-spy/chapter-36/",
    "#category": ("", "toonily", "chapter"),
    "#class"   : wpmadara.WPMadaraChapterExtractor,
    "#pattern" : r"https://toonily\.com/wp-content/uploads/WP-manga/data/manga_[^/]+/[^/]+/[^.]+\.\w+",
    "#count"   : 11,

    "manga"        : "Jinxed",
    "title"        : "",
    "chapter"      : 36,
    "tags"         : ["harem"],
    "lang"         : "en",
    "language"     : "English",
},

{
    "#url"     : "https://toonily.com/webtoon/such-a-cute-spy/chapter-1000000/",
    "#category": ("", "toonily", "chapter"),
    "#class"   : wpmadara.WPMadaraChapterExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://toonily.com/webtoon/such-a-cute-spy",
    "#category": ("", "toonily", "manga"),
    "#class"   : wpmadara.WPMadaraMangaExtractor,
    "#pattern" : r"https://toonily\.com/webtoon/such-a-cute-spy/chapter-\d+([_-].+)?/",
    "#count"   : ">= 13",

    "manga"      : "Such a Cute Spy",
    "author"     : ["Life of Ruin"],
    "artist"     : ["Ganghyeon Yeo"],
    "genres"     : [
        "Action",
        "Comedy",
        "Romance",
        "School Life",
    ],
    "rating"     : float,
    "status"     : "End",
    "lang"       : "en",
    "language"   : "English",
    "manga_alt"  : list,
},

{
    "#url"     : "https://toonily.com/webtoon/doesnotexist",
    "#category": ("", "toonily", "manga"),
    "#class"   : wpmadara.WPMadaraMangaExtractor,
    "#exception": exception.HttpError,
},

)
