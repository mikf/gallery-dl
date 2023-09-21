# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v01


__tests__ = (
{
    "#url"     : "https://the-collection.booru.org/index.php?page=post&s=list&tags=parody",
    "#category": ("gelbooru_v01", "thecollection", "tag"),
    "#class"   : gelbooru_v01.GelbooruV01TagExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "https://the-collection.booru.org/index.php?page=favorites&s=view&id=1166",
    "#category": ("gelbooru_v01", "thecollection", "favorite"),
    "#class"   : gelbooru_v01.GelbooruV01FavoriteExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://the-collection.booru.org/index.php?page=post&s=view&id=100520",
    "#category": ("gelbooru_v01", "thecollection", "post"),
    "#class"   : gelbooru_v01.GelbooruV01PostExtractor,
    "#sha1_url"    : "0329ac8588bb93cf242ca0edbe3e995b4ba554e8",
    "#sha1_content": "1e585874e7b874f7937df1060dd1517fef2f4dfb",
},

)
