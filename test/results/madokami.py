# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import madokami
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://manga.madokami.al/Manga/K/K_/K___/K%20-%20Memory%20of%20Red",
    "#class"   : madokami.MadokamiMangaExtractor,
    "#auth"    : True,
    "#results" : (
        "https://manga.madokami.al/Manga/K/K_/K___/K%20-%20Memory%20of%20Red/K%20-%20Memory%20of%20Red%20v01%20c01-02%20%281%20of%202%29.zip",
        "https://manga.madokami.al/Manga/K/K_/K___/K%20-%20Memory%20of%20Red/K%20-%20Memory%20of%20Red%20v01%20c03-05%20%282%20of%202%29.zip",
        "https://manga.madokami.al/Manga/K/K_/K___/K%20-%20Memory%20of%20Red/K%20-%20Memory%20of%20Red%20v02%20c06-10.zip",
        "https://manga.madokami.al/Manga/K/K_/K___/K%20-%20Memory%20of%20Red/K%20-%20Memory%20of%20Red%20v03%20c11-13%20%281%20of%202%29.zip",
        "https://manga.madokami.al/Manga/K/K_/K___/K%20-%20Memory%20of%20Red/K%20-%20Memory%20of%20Red%20v03%20c14-15%20%282%20of%202%29.zip",
    ),

    "chapter"       : {1, 3, 6, 11, 14},
    "chapter_end"   : {2, 5, 10, 13, 15},
    "chapter_id"    : range(57413, 57417),
    "chapter_string": r"re:v\d\d c\d\d-\d\d",
    "complete"      : True,
    "date"          : "type:datetime",
    "extension"     : "zip",
    "filename"      : r"re:K - Memory of Red .+",
    "manga"         : "K - Memory of Red",
    "path"          : r"re:/Manga/K/K_/K___/K%20-%20Memory%20of%20Red/K%20-%20Memory%20of%20Red%20.+\.zip",
    "size"          : range(57_986_253, 82_732_646),
    "volume"        : range(1, 3),
    "year"          : 2012,
    "author"        : [
        "GoHands",
        "GoRA",
        "KUROE Yui",
    ],
    "genre"         : [
        "Action",
        "Shoujo",
        "Supernatural",
    ],
    "tags"          : [
        "Bar/s",
        "Bartender/s",
        "Based on an Anime",
        "Bishounen",
        "Gang/s",
        "Multiple Protagonists",
        "Mysterious Protagonist",
        "Skateboarding",
        "Street Fighting",
        "Stubborn Protagonist",
    ],
},

{
    "#url"      : "https://manga.madokami.al/Manga/K/K_/K___/K%20-%20Memory%20of%20Red",
    "#comment"  : "no username & password",
    "#class"    : madokami.MadokamiMangaExtractor,
    "#auth"     : False,
    "#exception": exception.AuthRequired,
},

)
