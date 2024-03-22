# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v02


__tests__ = (
{
    "#url"     : "https://xbooru.com/index.php?page=post&s=list&tags=konoyan",
    "#category": ("gelbooru_v02", "xbooru", "tag"),
    "#class"   : gelbooru_v02.GelbooruV02TagExtractor,
    "#count"   : 25,
},

{
    "#url"     : "https://xbooru.com/index.php?page=pool&s=show&id=757",
    "#category": ("gelbooru_v02", "xbooru", "pool"),
    "#class"   : gelbooru_v02.GelbooruV02PoolExtractor,
    "#urls": (
        "https://img.xbooru.com/images/154/aeca160f8c7131f6a93033adac5416d7.jpeg",
        "https://img.xbooru.com/images/278/6185a8a71547568020e45e8319c02978.jpeg",
        "https://img.xbooru.com/images/524/0fc2b1e2e3cc8be259e9712ca3f48b0b.jpeg",
        "https://img.xbooru.com/images/253/74412b59a60fac5040c6cfe8efe7a625.jpeg",
        "https://img.xbooru.com/images/590/2eacd900958a467fb053b8a92145b55b.jpeg",
    ),
},

{
    "#url"     : "https://xbooru.com/index.php?page=favorites&s=view&id=45206",
    "#category": ("gelbooru_v02", "xbooru", "favorite"),
    "#class"   : gelbooru_v02.GelbooruV02FavoriteExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://xbooru.com/index.php?page=post&s=view&id=1025649",
    "#category": ("gelbooru_v02", "xbooru", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#pattern"     : r"https://img\.xbooru\.com/images/444/f3eda549ad8b9db244ac335c7406c92f\.jpeg",
    "#sha1_content": "086668afd445438d491ecc11cee3ac69b4d65530",
},

)
