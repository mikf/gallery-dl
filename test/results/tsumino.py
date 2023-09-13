# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tsumino


__tests__ = (
{
    "#url"     : "https://www.tsumino.com/entry/40996",
    "#category": ("", "tsumino", "gallery"),
    "#class"   : tsumino.TsuminoGalleryExtractor,
    "#pattern" : r"https://content.tsumino.com/parts/40996/\d+\?key=\w+",

    "title"     : r"re:Shikoshiko Daisuki Nightingale \+ Kaijou",
    "title_en"  : r"re:Shikoshiko Daisuki Nightingale \+ Kaijou",
    "title_jp"  : "シコシコ大好きナイチンゲール + 会場限定おまけ本",
    "gallery_id": 40996,
    "date"      : "dt:2018-06-29 00:00:00",
    "count"     : 42,
    "collection": "",
    "artist"    : ["Itou Life"],
    "group"     : ["Itou Life"],
    "parody"    : list,
    "characters": list,
    "tags"      : list,
    "type"      : "Doujinshi",
    "rating"    : float,
    "uploader"  : "sehki",
    "lang"      : "en",
    "language"  : "English",
    "thumbnail" : "https://content.tsumino.com/thumbs/40996/1",
},

{
    "#url"     : "https://www.tsumino.com/Book/Info/40996",
    "#category": ("", "tsumino", "gallery"),
    "#class"   : tsumino.TsuminoGalleryExtractor,
},

{
    "#url"     : "https://www.tsumino.com/Read/View/45834",
    "#category": ("", "tsumino", "gallery"),
    "#class"   : tsumino.TsuminoGalleryExtractor,
},

{
    "#url"     : "https://www.tsumino.com/Read/Index/45834",
    "#category": ("", "tsumino", "gallery"),
    "#class"   : tsumino.TsuminoGalleryExtractor,
},

{
    "#url"     : "https://www.tsumino.com/Books#?Character=Reimu+Hakurei",
    "#category": ("", "tsumino", "search"),
    "#class"   : tsumino.TsuminoSearchExtractor,
    "#pattern" : tsumino.TsuminoGalleryExtractor.pattern,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "http://www.tsumino.com/Books#~(Tags~(~(Type~7~Text~'Reimu*20Hakurei~Exclude~false)~(Type~'1~Text~'Pantyhose~Exclude~false)))#",
    "#category": ("", "tsumino", "search"),
    "#class"   : tsumino.TsuminoSearchExtractor,
    "#pattern" : tsumino.TsuminoGalleryExtractor.pattern,
    "#count"   : ">= 3",
},

)
