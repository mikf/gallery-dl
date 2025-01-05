# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import szurubooru


__tests__ = (
{
    "#url"     : "https://www.visuabusters.com/booru/posts/query=mincy_mouse",
    "#category": ("szurubooru", "visuabusters", "tag"),
    "#class"   : szurubooru.SzurubooruTagExtractor,
    "#pattern" : r"https://www\.visuabusters\.com/booru/data/posts/visuabusters_\d+_\w{16}\.\w+",
    "#count"   : range(2, 5),
},

{
    "#url"     : "https://www.visuabusters.com/booru/posts/query=",
    "#category": ("szurubooru", "visuabusters", "tag"),
    "#class"   : szurubooru.SzurubooruTagExtractor,
},

{
    "#url"     : "https://visuabusters.com/booru/posts",
    "#category": ("szurubooru", "visuabusters", "tag"),
    "#class"   : szurubooru.SzurubooruTagExtractor,
},

{
    "#url"     : "https://www.visuabusters.com/booru/post/2485",
    "#category": ("szurubooru", "visuabusters", "post"),
    "#class"   : szurubooru.SzurubooruPostExtractor,
    "#urls"        : "https://www.visuabusters.com/booru/data/posts/visuabusters_2485_ynmXFhNmBs3x0cCm.gif",
    "#sha1_content": "781fc0f063503d9d3f282558b9fcd69e37045e88",
},

)
