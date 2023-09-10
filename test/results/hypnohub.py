# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v02


__tests__ = (
{
    "#url"     : "https://hypnohub.net/index.php?page=post&s=list&tags=gonoike_biwa",
    "#category": ("gelbooru_v02", "hypnohub", "tag"),
    "#class"   : gelbooru_v02.GelbooruV02TagExtractor,
    "#sha1_url": "fe662b86d38c331fcac9c62af100167d404937dc",
},

{
    "#url"     : "https://hypnohub.net/index.php?page=pool&s=show&id=61",
    "#category": ("gelbooru_v02", "hypnohub", "pool"),
    "#class"   : gelbooru_v02.GelbooruV02PoolExtractor,
    "#count"   : 3,
    "#sha1_url": "d314826280073441a2da609f70ee814d1f4b9407",
},

{
    "#url"     : "https://hypnohub.net/index.php?page=favorites&s=view&id=43546",
    "#category": ("gelbooru_v02", "hypnohub", "favorite"),
    "#class"   : gelbooru_v02.GelbooruV02FavoriteExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://hypnohub.net/index.php?page=post&s=view&id=1439",
    "#category": ("gelbooru_v02", "hypnohub", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#options"     : {
        "tags" : True,
        "notes": True,
    },
    "#pattern"     : r"https://hypnohub\.net/images/90/24/90245c3c5250c2a8173255d3923a010b\.jpg",
    "#sha1_content": "5987c5d2354f22e5fa9b7ee7ce4a6f7beb8b2b71",

    "tags_artist"   : "brokenteapot",
    "tags_character": "hsien-ko",
    "tags_copyright": "capcom darkstalkers",
    "tags_general"  : str,
    "tags_metadata" : "dialogue text translated",
    "notes"         : [
        {
            "body"  : "Master Master Master Master Master Master",
            "height": 83,
            "id"    : 10577,
            "width" : 129,
            "x"     : 259,
            "y"     : 20,
        },
        {
            "body"  : "Response Response Response Response Response Response",
            "height": 86,
            "id"    : 10578,
            "width" : 125,
            "x"     : 126,
            "y"     : 20,
        },
        {
            "body"  : "Obedience Obedience Obedience Obedience Obedience Obedience",
            "height": 80,
            "id"    : 10579,
            "width" : 98,
            "x"     : 20,
            "y"     : 20,
        },
    ],
},

)
