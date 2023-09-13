# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import cyberdrop


__tests__ = (
{
    "#url"     : "https://cyberdrop.me/a/keKRjm4t",
    "#comment" : "images",
    "#category": ("lolisafe", "cyberdrop", "album"),
    "#class"   : cyberdrop.CyberdropAlbumExtractor,
    "#pattern" : r"https://fs-\d+\.cyberdrop\.to/.*\.(jpg|png|webp)$",

    "album_id"   : "keKRjm4t",
    "album_name" : "Fate (SFW)",
    "album_size" : 150069254,
    "count"      : 62,
    "date"       : "dt:2020-06-18 13:14:20",
    "description": "",
    "id"         : r"re:\w{8}",
},

{
    "#url"     : "https://cyberdrop.to/a/l8gIAXVD",
    "#comment" : "videos",
    "#category": ("lolisafe", "cyberdrop", "album"),
    "#class"   : cyberdrop.CyberdropAlbumExtractor,
    "#pattern" : r"https://fs-\d+\.cyberdrop\.to/.*\.mp4$",
    "#count"   : 31,

    "album_id"  : "l8gIAXVD",
    "album_name": "Achelois17 videos",
    "album_size": 652037121,
    "date"      : "dt:2020-06-16 15:40:44",
},

)
