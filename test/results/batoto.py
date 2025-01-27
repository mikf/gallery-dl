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

    "chapter"      : 8,
    "chapter_id"   : 1681030,
    "chapter_minor": "",
    "chapter_url"  : "8",
    "count"        : 66,
    "date"         : "dt:2021-05-15 18:51:37",
    "extension"    : "webp",
    "filename"     : str,
    "manga"        : "I Shall Master this Family! [Official]",
    "manga_id"     : 86408,
    "page"         : range(1, 66),
    "title"        : "Observing",
    "volume"       : 0,

},

{
    "#url"     : "https://bato.to/title/104929-86-eighty-six-official/1943513-vol_1-ch_5",
    "#comment" : "volume (vol) in url",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
    "#count"   : 7,

    "manga"  : "86--EIGHTY-SIX (Official)",
    "title"  : "The Spearhead Squadron's Power",
    "volume" : 1,
    "chapter": 5,
},

{
    "#url"     : "https://mto.to/chapter/2584460",
    "#comment" : "'-' in manga title (#5200)",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,

    "chapter"   : 9,
    "chapter_id": 2584460,
    "chapter_minor": "",
    "chapter_url": "9",
    "count"     : 18,
    "date"      : "dt:2023-11-26 11:01:12",
    "manga"     : "Isekai Teni shitara Aiken ga Saikyou ni narimashita - Silver Fenrir to Ore ga Isekai Kurashi wo Hajimetara (Official)",
    "manga_id"  : 126793,
    "title"     : "",
    "volume"    : 0
},

{
    "#url"     : "https://bato.to/title/90710-new-suitor-for-the-abandoned-wife/2089747-ch_76",
    "#comment" : "duplicate info in chapter_minor / title (#5988)",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,

    "chapter"      : 76,
    "chapter_id"   : 2089747,
    "chapter_minor": "",
    "chapter_url"  : "76",
    "title"        : "Side Story 4 [END]",
},

{
    "#url"     : "https://bato.to/title/115494-today-with-you/2631897-ch_38",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,

    "chapter"       : 37,
    "chapter_id"    : 2631897,
    "chapter_minor" : "",
    "chapter_string": "S1 Episode 37 (End of season)",
    "chapter_url"   : "38",
    "count"         : 69,
    "date"          : "dt:2023-12-20 17:31:18",
    "manga"         : "Today With You",
    "manga_id"      : 115494,
    "title"         : "",
    "volume"        : 1,
},

{
    "#url"     : "https://bato.to/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://bato.to/chapter/1681030",
    "#comment" : "v2 URL",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://bato.to/title/113742-futsutsuka-na-akujo-de-wa-gozaimasu-ga-suuguu-chouso-torikae-den-official",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 21",

    "chapter"      : int,
    "chapter_minor": str,
    "date"         : "type:datetime",
    "manga"        : "Futsutsuka na Akujo de wa Gozaimasu ga - Suuguu Chouso Torikae Den",
    "manga_id"     : 113742,
},

{
    "#url"     : "https://bato.to/title/104929-86-eighty-six-official",
    "#comment" : "Manga with number in name",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 18",

    "manga": "86--EIGHTY-SIX (Official)",
},

{
    "#url"     : "https://bato.to/title/140046-the-grand-duke-s-fox-princess-mgchan",
    "#comment" : "Non-English translation (Indonesian)",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 29",

    "manga": "The Grand Duke’s Fox Princess [cont by LUNABY]",
},

{
    "#url"     : "https://bato.to/title/134270-removed",
    "#comment" : "Deleted/removed manga",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://bato.to/title/86408-i-shall-master-this-family-official",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
},

{
    "#url"     : "https://bato.to/series/86408/i-shall-master-this-family-official",
    "#comment" : "v2 URL",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
},

{
    "#url"     : "https://dto.to/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://hto.to/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://mto.to/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://wto.to/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://mangatoto.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://mangatoto.net/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://mangatoto.org/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://batocomic.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://batocomic.net/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://batocomic.org/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://readtoto.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://readtoto.net/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://readtoto.org/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://xbato.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://xbato.net/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://xbato.org/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://zbato.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://zbato.net/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://zbato.org/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://comiko.net/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://comiko.org/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://batotoo.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://batotwo.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://battwo.com/title/86408/1681030",
    "#category": ("", "batoto", "chapter"),
    "#class"   : batoto.BatotoChapterExtractor,
},

)
