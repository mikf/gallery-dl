# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import photos18


__tests__ = (
{
    "#url"     : "https://www.photos18.com/v/3BXQy",
    "#category": ("", "photos18", "album"),
    "#class"   : photos18.Photos18AlbumExtractor,
    "#count"   : 12,
    "#sha1_url": "2f9442f34f31bafdd6d57f4954674348b38ef284",

    "title"        : "Peachmilky Nanami, Mami Rent-a-Girlfriend",
    "category_id"  : 8,
    "category_name": "COSPLAY",
},

{
    "#url"     : "https://www.photos18.com/v/jMMn2",
    "#category": ("", "photos18", "album"),
    "#class"   : photos18.Photos18AlbumExtractor,
    "#count"   : 36,

    "title"        : "姐姐說兒童節幫我\"轉大人\"Kenna James - Stepbro Accidentally Cums In Stepsister's Pussy",
    "category_id"  : 1,
    "category_name": "歐美寫真",
},

{
    "#url"     : "https://www.photos18.com",
    "#category": ("", "photos18", "list"),
    "#class"   : photos18.Photos18ListExtractor,
    "#range"   : "1-200",
    "#count"   : 200,
},

)
