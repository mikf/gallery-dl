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
    "#count"   : 11,
},

{
    "#url"     : "https://xbooru.com/index.php?page=pool&s=show&id=757",
    "#category": ("gelbooru_v02", "xbooru", "pool"),
    "#class"   : gelbooru_v02.GelbooruV02PoolExtractor,
    "#count"   : 5,
    "#sha1_url": "ceeac56c179ec72301bd0b6add6355a138fdea01",
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
