# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import photovogue


__tests__ = (
{
    "#url"     : "https://www.vogue.com/photovogue/photographers/221252",
    "#category": ("", "photovogue", "user"),
    "#class"   : photovogue.PhotovogueUserExtractor,
},

{
    "#url"     : "https://vogue.com/photovogue/photographers/221252",
    "#category": ("", "photovogue", "user"),
    "#class"   : photovogue.PhotovogueUserExtractor,
    "#pattern" : "https://images.vogue.it/Photovogue/[^/]+_gallery.jpg",

    "date"           : "type:datetime",
    "favorite_count" : int,
    "favorited"      : list,
    "id"             : int,
    "image_id"       : str,
    "is_favorite"    : False,
    "orientation"    : r"re:portrait|landscape",
    "photographer"   : {
        "biography"     : "Born in 1995. Live in Bologna.",
        "city"          : "Bologna",
        "country_id"    : 106,
        "favoritedCount": int,
        "id"            : 221252,
        "isGold"        : bool,
        "isPro"         : bool,
        "latitude"      : str,
        "longitude"     : str,
        "name"          : "Arianna Mattarozzi",
        "user_id"       : "38cb0601-4a85-453c-b7dc-7650a037f2ab",
        "websites"      : list,
    },
    "photographer_id": 221252,
    "tags"           : list,
    "title"          : str,
},

)
