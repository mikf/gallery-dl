# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lensdump


__tests__ = (
{
    "#url"     : "https://lensdump.com/a/1IhJr",
    "#category": ("", "lensdump", "album"),
    "#class"   : lensdump.LensdumpAlbumExtractor,
    "#pattern" : r"https://[abcd]\.l3n\.co/i/tq\w{4}\.png",

    "extension": "png",
    "name"     : str,
    "num"      : int,
    "title"    : str,
    "url"      : str,
    "width"    : int,
},

{
    "#url"     : "https://lensdump.com/vstar925/albums",
    "#category": ("", "lensdump", "albums"),
    "#class"   : lensdump.LensdumpAlbumsExtractor,
},

{
    "#url"     : "https://lensdump.com/i/tyoAyM",
    "#category": ("", "lensdump", "image"),
    "#class"   : lensdump.LensdumpImageExtractor,
    "#urls"        : "https://c.l3n.co/i/tyoAyM.webp",
    "#sha1_content": "1aa749ed2c0cf679ec8e1df60068edaf3875de46",

    "date"     : "dt:2022-08-01 08:24:28",
    "extension": "webp",
    "filename" : "tyoAyM",
    "height"   : 400,
    "id"       : "tyoAyM",
    "title"    : "MYOBI clovis bookcaseset",
    "url"      : "https://c.l3n.co/i/tyoAyM.webp",
    "width"    : 620,
},

{
    "#url"     : "https://c.l3n.co/i/tyoAyM.webp",
    "#category": ("", "lensdump", "image"),
    "#class"   : lensdump.LensdumpImageExtractor,
    "#urls"    : "https://c.l3n.co/i/tyoAyM.webp",

    "date"     : "dt:2022-08-01 08:24:28",
    "extension": "webp",
    "filename" : "tyoAyM",
    "height"   : 400,
    "id"       : "tyoAyM",
    "title"    : "MYOBI clovis bookcaseset",
    "url"      : "https://c.l3n.co/i/tyoAyM.webp",
    "width"    : 620,
},

{
    "#url"     : "https://i.lensdump.com/i/tyoAyM",
    "#category": ("", "lensdump", "image"),
    "#class"   : lensdump.LensdumpImageExtractor,
},

{
    "#url"     : "https://i3.lensdump.com/i/tyoAyM",
    "#category": ("", "lensdump", "image"),
    "#class"   : lensdump.LensdumpImageExtractor,
},

)
