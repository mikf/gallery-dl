# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangoxo


__tests__ = (
{
    "#url"     : "https://www.mangoxo.com/album/lzVOv1Q9",
    "#category": ("", "mangoxo", "album"),
    "#class"   : mangoxo.MangoxoAlbumExtractor,
    "#sha1_url": "ad921fe62663b06e7d73997f7d00646cab7bdd0d",

    "channel": {
        "id"   : "gaxO16d8",
        "name" : "Phoenix",
        "cover": str,
    },
    "album"  : {
        "id"         : "lzVOv1Q9",
        "name"       : r"re:池永康晟 Ikenaga Yasunari 透出古朴",
        "date"       : "dt:2019-03-22 14:42:00",
        "description": str,
    },
    "id"     : int,
    "num"    : int,
    "count"  : 65,
},

{
    "#url"     : "https://www.mangoxo.com/phoenix/album",
    "#category": ("", "mangoxo", "channel"),
    "#class"   : mangoxo.MangoxoChannelExtractor,
    "#pattern" : mangoxo.MangoxoAlbumExtractor.pattern,
    "#range"   : "1-30",
    "#count"   : "> 20",
},

)
