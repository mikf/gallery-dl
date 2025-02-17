# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import danbooru


__tests__ = (
{
    "#url"     : "https://bleachbooru.org/posts?tags=dora_v_nu&z=1",
    "#category": ("Danbooru", "bleachbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#pattern" : r"https://bleachbooru\.org/data/original/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.\w+",
    "#count"   : ">=5",
},

{
    "#url"     : "https://bleachbooru.org/pools/60",
    "#category": ("Danbooru", "bleachbooru", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
    "#count"   : 5,
},

{
    "#url"     : "https://bleachbooru.org/posts/94297",
    "#category": ("Danbooru", "bleachbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#sha1_content": "abe9b6cad06bd3d37212d71ac309affbbe6f8703",
},

{
    "#url"     : "https://bleachbooru.org/explore/posts/popular",
    "#category": ("Danbooru", "bleachbooru", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
},

)
