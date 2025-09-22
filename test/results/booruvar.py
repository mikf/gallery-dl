# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import danbooru


__tests__ = (
{
    "#url"     : "https://booru.borvar.art/posts?tags=chibi&z=1",
    "#category": ("Danbooru", "booruvar", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#pattern" : r"https://booru\.borvar\.art/data/original/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.\w+",
    "#count"   : ">= 3",
},

{
    "#url"     : "https://booru.borvar.art/pools/2",
    "#category": ("Danbooru", "booruvar", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
    "#count"   : 4,
    "#sha1_url": "77fa3559a3fc919f72611f4e3dd0f919d19d3e0d",
},

{
    "#url"     : "https://booru.borvar.art/posts/1487",
    "#category": ("Danbooru", "booruvar", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#sha1_content": "91273ac1ea413a12be468841e2b5804656a50bff",
},

{
    "#url"     : "https://booru.borvar.art/explore/posts/popular",
    "#category": ("Danbooru", "booruvar", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
},

{
    "#url"     : "https://booru.borvar.art/posts/random?tags=chibi&z=1",
    "#category": ("Danbooru", "booruvar", "random"),
    "#class"   : danbooru.DanbooruRandomExtractor,
},

{
    "#url"     : "https://booru.borvar.art/posts/random",
    "#category": ("Danbooru", "booruvar", "random"),
    "#class"   : danbooru.DanbooruRandomExtractor,
},

)
