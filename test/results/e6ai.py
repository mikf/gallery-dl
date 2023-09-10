# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import e621


__tests__ = (
{
    "#url"     : "https://e6ai.net/posts?tags=anry",
    "#category": ("E621", "e6ai", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e6ai.net/post/index/1/anry",
    "#category": ("E621", "e6ai", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e6ai.net/post?tags=anry",
    "#category": ("E621", "e6ai", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e6ai.net/pools/3",
    "#category": ("E621", "e6ai", "pool"),
    "#class"   : e621.E621PoolExtractor,
    "#sha1_url": "a6d1ad67a3fa9b9f73731d34d5f6f26f7e85855f",
},

{
    "#url"     : "https://e6ai.net/pool/show/3",
    "#category": ("E621", "e6ai", "pool"),
    "#class"   : e621.E621PoolExtractor,
},

{
    "#url"     : "https://e6ai.net/posts/23",
    "#category": ("E621", "e6ai", "post"),
    "#class"   : e621.E621PostExtractor,
    "#sha1_url"    : "3c85a806b3d9eec861948af421fe0e8ad6b8f881",
    "#sha1_content": "a05a484e4eb64637d56d751c02e659b4bc8ea5d5",
},

{
    "#url"     : "https://e6ai.net/post/show/23",
    "#category": ("E621", "e6ai", "post"),
    "#class"   : e621.E621PostExtractor,
},

{
    "#url"     : "https://e6ai.net/explore/posts/popular",
    "#category": ("E621", "e6ai", "popular"),
    "#class"   : e621.E621PopularExtractor,
},

{
    "#url"     : "https://e6ai.net/favorites",
    "#category": ("E621", "e6ai", "favorite"),
    "#class"   : e621.E621FavoriteExtractor,
},

)
