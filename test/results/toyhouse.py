# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import toyhouse


__tests__ = (
{
    "#url"     : "https://www.toyhou.se/d-floe/art",
    "#category": ("", "toyhouse", "art"),
    "#class"   : toyhouse.ToyhouseArtExtractor,
    "#pattern" : r"https://f\d+\.toyhou\.se/file/f\d+-toyhou-se/images/\d+_\w+\.\w+$",
    "#range"   : "1-30",
    "#count"   : 30,

    "artists"   : list,
    "characters": list,
    "date"      : "type:datetime",
    "hash"      : r"re:\w+",
    "id"        : r"re:\d+",
    "url"       : str,
    "user"      : "d-floe",
},

{
    "#url"     : "https://www.toyhou.se/kroksoc/art",
    "#comment" : "protected by Content Warning",
    "#category": ("", "toyhouse", "art"),
    "#class"   : toyhouse.ToyhouseArtExtractor,
    "#count"   : ">= 19",
},

{
    "#url"     : "https://toyhou.se/~images/40587320",
    "#category": ("", "toyhouse", "image"),
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#sha1_content": "058ec8427977ab432c4cc5be5a6dd39ce18713ef",

    "artists"   : ["d-floe"],
    "characters": ["Sumi"],
    "date"      : "dt:2021-10-08 01:32:47",
    "extension" : "png",
    "filename"  : "40587320_TT1NaBUr3FLkS1p",
    "hash"      : "TT1NaBUr3FLkS1p",
    "id"        : "40587320",
    "url"       : "https://f2.toyhou.se/file/f2-toyhou-se/images/40587320_TT1NaBUr3FLkS1p.png",
},

{
    "#url"     : "https://f2.toyhou.se/file/f2-toyhou-se/watermarks/36817425_bqhGcwcnU.png?1625561467",
    "#comment" : "direct link, multiple artists",
    "#category": ("", "toyhouse", "image"),
    "#class"   : toyhouse.ToyhouseImageExtractor,

    "artists"   : [
        "http://aminoapps.com/p/92sf3z",
        "kroksoc (Color)",
    ],
    "characters": ["Reiichi❀"],
    "date"      : "dt:2021-07-03 20:02:02",
    "hash"      : "bqhGcwcnU",
    "id"        : "36817425",
},

{
    "#url"     : "https://f2.toyhou.se/file/f2-toyhou-se/images/40587320_TT1NaBUr3FLkS1p.png",
    "#category": ("", "toyhouse", "image"),
    "#class"   : toyhouse.ToyhouseImageExtractor,
},

)
