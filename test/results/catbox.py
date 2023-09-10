# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import catbox


__tests__ = (
{
    "#url"     : "https://catbox.moe/c/1igcbe",
    "#category": ("", "catbox", "album"),
    "#class"   : catbox.CatboxAlbumExtractor,
    "#pattern"     : r"https://files\.catbox\.moe/\w+\.\w{3}$",
    "#count"       : 3,
    "#sha1_url"    : "35866a88c29462814f103bc22ec031eaeb380f8a",
    "#sha1_content": "70ddb9de3872e2d17cc27e48e6bf395e5c8c0b32",

    "album_id"   : "1igcbe",
    "album_name" : "test",
    "date"       : "dt:2022-08-18 00:00:00",
    "description": "album test &>",
},

{
    "#url"     : "https://www.catbox.moe/c/cd90s1",
    "#category": ("", "catbox", "album"),
    "#class"   : catbox.CatboxAlbumExtractor,
},

{
    "#url"     : "https://catbox.moe/c/w7tm47#",
    "#category": ("", "catbox", "album"),
    "#class"   : catbox.CatboxAlbumExtractor,
},

{
    "#url"     : "https://files.catbox.moe/8ih3y7.png",
    "#category": ("", "catbox", "file"),
    "#class"   : catbox.CatboxFileExtractor,
    "#pattern"     : r"^https://files\.catbox\.moe/8ih3y7\.png$",
    "#count"       : 1,
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",
},

{
    "#url"     : "https://litter.catbox.moe/t8v3n9.png",
    "#category": ("", "catbox", "file"),
    "#class"   : catbox.CatboxFileExtractor,
},

{
    "#url"     : "https://de.catbox.moe/bjdmz1.jpg",
    "#category": ("", "catbox", "file"),
    "#class"   : catbox.CatboxFileExtractor,
},

)
