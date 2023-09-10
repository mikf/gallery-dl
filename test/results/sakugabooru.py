# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import moebooru


__tests__ = (
{
    "#url"     : "https://www.sakugabooru.com/post/show/125570",
    "#category": ("moebooru", "sakugabooru", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
},

{
    "#url"     : "https://www.sakugabooru.com/post?tags=nichijou",
    "#category": ("moebooru", "sakugabooru", "tag"),
    "#class"   : moebooru.MoebooruTagExtractor,
},

{
    "#url"     : "https://www.sakugabooru.com/pool/show/54",
    "#category": ("moebooru", "sakugabooru", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
},

{
    "#url"     : "https://www.sakugabooru.com/post/popular_recent",
    "#category": ("moebooru", "sakugabooru", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
},

)
