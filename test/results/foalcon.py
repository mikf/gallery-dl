# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import szurubooru


__tests__ = (
{
    "#url"     : "https://booru.foalcon.com/posts/query=simple_background",
    "#category": ("szurubooru", "foalcon", "tag"),
    "#class"   : szurubooru.SzurubooruTagExtractor,
    "#pattern" : r"https://booru\.foalcon\.com/data/posts/\d+_[0-9a-f]{16}\.\w+",
    "#range"   : "1-150",
    "#count"   : 150,
},

{
    "#url"     : "https://booru.foalcon.com/post/30092",
    "#category": ("szurubooru", "foalcon", "post"),
    "#class"   : szurubooru.SzurubooruPostExtractor,
    "#pattern"     : r"https://booru\.foalcon\.com/data/posts/30092_b7d56e941888b624\.png",
    "#sha1_url"    : "dad4d4c67d87cd9a4ac429b3414747c27a95d5cb",
    "#sha1_content": "86d1514c0ca8197950cc4b74e7a59b2dc76ebf9c",
},

)
