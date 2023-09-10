# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v02


__tests__ = (
{
    "#url"     : "https://realbooru.com/index.php?page=post&s=list&tags=wine",
    "#category": ("gelbooru_v02", "realbooru", "tag"),
    "#class"   : gelbooru_v02.GelbooruV02TagExtractor,
    "#count"   : ">= 64",
},

{
    "#url"     : "https://realbooru.com/index.php?page=pool&s=show&id=1",
    "#category": ("gelbooru_v02", "realbooru", "pool"),
    "#class"   : gelbooru_v02.GelbooruV02PoolExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://realbooru.com/index.php?page=favorites&s=view&id=274",
    "#category": ("gelbooru_v02", "realbooru", "favorite"),
    "#class"   : gelbooru_v02.GelbooruV02FavoriteExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://realbooru.com/index.php?page=post&s=view&id=668483",
    "#category": ("gelbooru_v02", "realbooru", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#options"     : {"tags": True},
    "#pattern"     : r"https://realbooru\.com//?images/dc/b5/dcb5c0ce9ec0bf74a6930608985f4719\.jpeg",
    "#sha1_content": "7f5873ce3b6cd295ea2e81fcb49583098ea9c8da",

    "tags_general": "1girl blonde blonde_hair blue_eyes cute female female_only looking_at_viewer smile solo solo_female teeth",
    "tags_model"  : "jennifer_lawrence",
},

)
