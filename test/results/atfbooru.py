# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import danbooru


__tests__ = (
{
    "#url"     : "https://booru.allthefallen.moe/posts?tags=yume_shokunin",
    "#category": ("Danbooru", "atfbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#count"   : 12,
},

{
    "#url"     : "https://booru.allthefallen.moe/pools/9",
    "#category": ("Danbooru", "atfbooru", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
    "#count"   : 6,
    "#sha1_url": "902549ffcdb00fe033c3f63e12bc3cb95c5fd8d5",
},

{
    "#url"     : "https://booru.allthefallen.moe/posts/22",
    "#category": ("Danbooru", "atfbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#sha1_content": "21dda68e1d7e0a554078e62923f537d8e895cac8",
},

{
    "#url"     : "https://booru.allthefallen.moe/explore/posts/popular",
    "#category": ("Danbooru", "atfbooru", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
},

{
    "#url"     : "https://booru.allthefallen.moe/posts/random?tags=yume_shokunin",
    "#category": ("Danbooru", "atfbooru", "random"),
    "#class"   : danbooru.DanbooruRandomExtractor,
},

{
    "#url"     : "https://booru.allthefallen.moe/posts/random",
    "#category": ("Danbooru", "atfbooru", "random"),
    "#class"   : danbooru.DanbooruRandomExtractor,
},

)
