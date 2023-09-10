# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import moebooru


__tests__ = (
{
    "#url"     : "https://lolibooru.moe/post/show/281305/",
    "#category": ("moebooru", "lolibooru", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
    "#options"     : {"notes": True},
    "#sha1_content": "a331430223ffc5b23c31649102e7d49f52489b57",

    "notes": list,
},

{
    "#url"     : "https://lolibooru.moe/post/show/287835",
    "#category": ("moebooru", "lolibooru", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
},

{
    "#url"     : "https://lolibooru.moe/post?tags=ruu_%28tksymkw%29",
    "#category": ("moebooru", "lolibooru", "tag"),
    "#class"   : moebooru.MoebooruTagExtractor,
},

{
    "#url"     : "https://lolibooru.moe/pool/show/239",
    "#category": ("moebooru", "lolibooru", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
},

{
    "#url"     : "https://lolibooru.moe/post/popular_recent",
    "#category": ("moebooru", "lolibooru", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
},

)
