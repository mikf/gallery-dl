# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bilibili


__tests__ = (
{
    "#url"  : "https://www.bilibili.com/opus/988425412565532689",
    "#class": bilibili.BilibiliArticleExtractor,
    "#urls" : (
        "http://i0.hdslb.com/bfs/new_dyn/311264c4dcf45261f7d7a7fe451b05b9405279279.png",
        "http://i0.hdslb.com/bfs/new_dyn/b60d8bc6996529613d617443a12c0a93405279279.png",
        "http://i0.hdslb.com/bfs/new_dyn/d4494543210d9eee5310e11dc62581e4405279279.png",
        "http://i0.hdslb.com/bfs/new_dyn/45268e63086b2d99811b2e6490130937405279279.png",
    ),

    "count"    : 4,
    "detail"   : dict,
    "extension": "png",
    "filename" : str,
    "height"   : 800,
    "id"       : "988425412565532689",
    "isClient" : False,
    "isPreview": False,
    "num"      : range(1, 4),
    "size"     : float,
    "theme"    : str,
    "themeMode": "light",
    "url"      : str,
    "username" : "平平出击",
    "width"    : 800,
},

{
    "#url"    : "https://www.bilibili.com/opus/977981688469520405",
    "#comment": "'module_top' file (#6687)",
    "#class"  : bilibili.BilibiliArticleExtractor,
    "#urls"   : (
        "http://i0.hdslb.com/bfs/new_dyn/c74018e8272c56a6c28a1a1dc3c586311242656443.jpg",
    ),

    "count"    : 1,
    "filename" : "c74018e8272c56a6c28a1a1dc3c586311242656443",
    "extension": "jpg",
    "width"    : 712,
    "height"   : 1068,
    "size"     : 115.80999755859375,
    "id"       : "977981688469520405",
    "username" : "诗月饼",
},

{
    "#url"    : "https://space.bilibili.com/405279279/article",
    "#class"  : bilibili.BilibiliUserArticlesExtractor,
    "#pattern": bilibili.BilibiliArticleExtractor.pattern,
    "#count"  : range(50, 100),
},

{
    "#url"    : "https://space.bilibili.com/405279279/upload/opus",
    "#class"  : bilibili.BilibiliUserArticlesExtractor,
},

)
