# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nsfwalbum


__tests__ = (
{
    "#url"     : "https://nsfwalbum.com/album/401611",
    "#category": ("", "nsfwalbum", "album"),
    "#class"   : nsfwalbum.NsfwalbumAlbumExtractor,
    "#range"        : "1-5",
    "#results"      : (
        "https://img70.imgspice.com/i/05457/mio2bu5xbrxe.jpg",
        "https://img70.imgspice.com/i/05457/zgpxa8kr4h1d.jpg",
        "https://img70.imgspice.com/i/05457/3379nxsm9lx8.jpg",
        "https://img70.imgspice.com/i/05457/pncrkhspuoa3.jpg",
        "https://img70.imgspice.com/i/05457/128b2odt216a.jpg",
    ),

    "album_id" : 401611,
    "extension": "jpg",
    "filename" : str,
    "height"   : range(1365, 2048),
    "id"       : int,
    "models"   : [],
    "num"      : range(1, 5),
    "studio"   : "Met-Art",
    "title"    : "Met-Art - Katherine A - Difuza 25.05.2014 (134 photos)(4368 X 2912)",
    "width"    : range(1365, 2048),
},

)
