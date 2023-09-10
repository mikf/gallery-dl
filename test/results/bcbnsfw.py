# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import szurubooru


__tests__ = (
{
    "#url"     : "https://booru.bcbnsfw.space/posts/query=simple_background",
    "#category": ("szurubooru", "bcbnsfw", "tag"),
    "#class"   : szurubooru.SzurubooruTagExtractor,
},

{
    "#url"     : "https://booru.bcbnsfw.space/post/1599",
    "#category": ("szurubooru", "bcbnsfw", "post"),
    "#class"   : szurubooru.SzurubooruPostExtractor,
    "#pattern"     : r"https://booru\.bcbnsfw\.space/data/posts/1599_53784518e92086bd\.png",
    "#sha1_content": "0c38fc612ba1f03950fad31c4f80a1fccdab1096",
},

)
