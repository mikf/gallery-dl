# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v02


__tests__ = (
{
    "#url"     : "https://tbib.org/index.php?page=post&s=list&tags=yuyaiyaui",
    "#category": ("gelbooru_v02", "tbib", "tag"),
    "#class"   : gelbooru_v02.GelbooruV02TagExtractor,
    "#count"   : ">= 120",
},

{
    "#url"     : "https://tbib.org/index.php?page=favorites&s=view&id=7881",
    "#category": ("gelbooru_v02", "tbib", "favorite"),
    "#class"   : gelbooru_v02.GelbooruV02FavoriteExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://tbib.org/index.php?page=post&s=view&id=9233957",
    "#category": ("gelbooru_v02", "tbib", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#sha1_url"    : "5a6ebe07bfff8e6d27f7c30b5480f27abcb577d2",
    "#sha1_content": "1c3831b6fbaa4686e3c79035b5d98460b1c85c43",
},

)
