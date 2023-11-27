# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import danbooru


__tests__ = (
{
    "#url"     : "https://aibooru.online/posts?tags=center_frills&z=1",
    "#category": ("Danbooru", "aibooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#pattern" : r"https://cdn\.aibooru\.download/original/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.\w+",
    "#count"   : ">= 50",
},

{
    "#url"     : "https://safe.aibooru.online/posts?tags=center_frills",
    "#category": ("Danbooru", "aibooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://aibooru.online/pools/1",
    "#category": ("Danbooru", "aibooru", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
},

{
    "#url"     : "https://aibooru.online/posts/1",
    "#category": ("Danbooru", "aibooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#sha1_content": "54d548743cd67799a62c77cbae97cfa0fec1b7e9",
},

{
    "#url"     : "https://aibooru.online/explore/posts/popular",
    "#category": ("Danbooru", "aibooru", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
},

)
