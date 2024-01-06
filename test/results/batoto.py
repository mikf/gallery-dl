# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import batoto
from gallery_dl import exception

__tests__ = (
{
    "#url"     : "https://bato.to/title/86408-i-shall-master-this-family-official/1681030-ch_8",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
    "#count"   : 66,

    "manga"        : "I Shall Master this Family! [Official]",
    "title"        : "Observing",
    "chapter"      : 8,
},
{
    "#url"     : "https://bato.to/title/104929-86-eighty-six-official/1943513-vol_1-ch_5",
    "#comment" : "volume (vol) in url",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
    "#count"   : 7,

    "manga"        : "86--EIGHTY-SIX (Official)",
    "title"        : "The Spearhead Squadron's Power",
    "volume"       : 1,
    "chapter"      : 5,
},
{
    "#url"     : "https://bato.to/title/113742-futsutsuka-na-akujo-de-wa-gozaimasu-ga-suuguu-chouso-torikae-den-official",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 21",

    "manga"        : "Futsutsuka na Akujo de wa Gozaimasu ga - Suuguu Chouso Torikae Den (Official)",
},
{
    "#url"     : "https://bato.to/title/104929-86-eighty-six-official",
    "#comment" : "Manga with number in name",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 18",

    "manga"        : "86--EIGHTY-SIX (Official)",
},
{
    "#url"     : "https://bato.to/title/140046-the-grand-duke-s-fox-princess-mgchan",
    "#comment" : "Non-English translation (Indonesian)",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 29",

    "manga"        : "The Grand Duke’s Fox Princess ⎝⎝MGCHAN⎠⎠",
},
{
    "#url"     : "https://bato.to/title/134270-removed",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#exception": exception.StopExtraction,
}
)
