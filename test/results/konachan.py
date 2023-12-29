# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import moebooru
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://konachan.com/post/show/205189",
    "#category": ("moebooru", "konachan", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
    "#options"     : {"tags": True},
    "#sha1_content": "674e75a753df82f5ad80803f575818b8e46e4b65",

    "tags_artist"   : "patata",
    "tags_character": "clownpiece",
    "tags_copyright": "touhou",
    "tags_general"  : str,
},

{
    "#url"     : "https://konachan.net/post/show/205189",
    "#category": ("moebooru", "konachan", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
},

{
    "#url"     : "https://konachan.com/post?tags=patata",
    "#category": ("moebooru", "konachan", "tag"),
    "#class"   : moebooru.MoebooruTagExtractor,
    "#sha1_content": "838cfb815e31f48160855435655ddf7bfc4ecb8d",
},

{
    "#url"     : "https://konachan.com/post?tags=",
    "#comment" : "empty 'tags' (#4354)",
    "#category": ("moebooru", "konachan", "tag"),
    "#class"   : moebooru.MoebooruTagExtractor,
},

{
    "#url"     : "https://konachan.net/post?tags=patata",
    "#category": ("moebooru", "konachan", "tag"),
    "#class"   : moebooru.MoebooruTagExtractor,
},

{
    "#url"     : "https://konachan.com/pool/show/95",
    "#category": ("moebooru", "konachan", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
    "#sha1_content": "cf0546e38a93c2c510a478f8744e60687b7a8426",
},

{
    "#url"     : "https://konachan.com/pool/show/95",
    "#comment" : "'metadata' option (#4646)",
    "#category": ("moebooru", "konachan", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
    "#options"  : {"metadata": True},
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://konachan.net/pool/show/95",
    "#category": ("moebooru", "konachan", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
},

{
    "#url"     : "https://konachan.com/post/popular_by_month?month=11&year=2010",
    "#category": ("moebooru", "konachan", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
    "#count"   : 20,
},

{
    "#url"     : "https://konachan.com/post/popular_recent",
    "#category": ("moebooru", "konachan", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
},

{
    "#url"     : "https://konachan.net/post/popular_recent",
    "#category": ("moebooru", "konachan", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
},

)
