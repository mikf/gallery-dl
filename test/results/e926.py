# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import e621


__tests__ = (
{
    "#url"     : "https://e926.net/posts?tags=anry",
    "#category": ("E621", "e926", "tag"),
    "#class"   : e621.E621TagExtractor,
    "#sha1_url"    : "12198b275c62ffe2de67cca676c8e64de80c425d",
    "#sha1_content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
},

{
    "#url"     : "https://e926.net/post/index/1/anry",
    "#category": ("E621", "e926", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e926.net/post?tags=anry",
    "#category": ("E621", "e926", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e926.net/pools/73",
    "#category": ("E621", "e926", "pool"),
    "#class"   : e621.E621PoolExtractor,
    "#sha1_url"    : "6936f1b6a18c5c25bee7cad700088dbc2503481b",
    "#sha1_content": "91abe5d5334425d9787811d7f06d34c77974cd22",
},

{
    "#url"     : "https://e926.net/pool/show/73",
    "#category": ("E621", "e926", "pool"),
    "#class"   : e621.E621PoolExtractor,
},

{
    "#url"     : "https://e926.net/posts/535",
    "#category": ("E621", "e926", "post"),
    "#class"   : e621.E621PostExtractor,
    "#sha1_url"    : "17aec8ebd8fab098d321adcb62a2db59dab1f4bf",
    "#sha1_content": "66f46e96a893fba8e694c4e049b23c2acc9af462",
},

{
    "#url"     : "https://e926.net/post/show/535",
    "#category": ("E621", "e926", "post"),
    "#class"   : e621.E621PostExtractor,
},

{
    "#url"     : "https://e926.net/explore/posts/popular",
    "#category": ("E621", "e926", "popular"),
    "#class"   : e621.E621PopularExtractor,
},

{
    "#url"     : "https://e926.net/explore/posts/popular?date=2019-06-01&scale=month",
    "#category": ("E621", "e926", "popular"),
    "#class"   : e621.E621PopularExtractor,
    "#pattern" : r"https://static\d.e926.net/data/../../[0-9a-f]+",
    "#count"   : ">= 70",
},

{
    "#url"     : "https://e926.net/favorites",
    "#category": ("E621", "e926", "favorite"),
    "#class"   : e621.E621FavoriteExtractor,
},

{
    "#url"     : "https://e926.net/favorites?page=2&user_id=53275",
    "#category": ("E621", "e926", "favorite"),
    "#class"   : e621.E621FavoriteExtractor,
    "#pattern" : r"https://static\d.e926.net/data/../../[0-9a-f]+",
    "#count"   : "> 260",
},

)
