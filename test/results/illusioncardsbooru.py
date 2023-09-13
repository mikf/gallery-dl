# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v01


__tests__ = (
{
    "#url"     : "https://illusioncards.booru.org/index.php?page=post&s=list&tags=koikatsu",
    "#category": ("gelbooru_v01", "illusioncardsbooru", "tag"),
    "#class"   : gelbooru_v01.GelbooruV01TagExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "https://illusioncards.booru.org/index.php?page=favorites&s=view&id=84887",
    "#category": ("gelbooru_v01", "illusioncardsbooru", "favorite"),
    "#class"   : gelbooru_v01.GelbooruV01FavoriteExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://illusioncards.booru.org/index.php?page=post&s=view&id=82746",
    "#category": ("gelbooru_v01", "illusioncardsbooru", "post"),
    "#class"   : gelbooru_v01.GelbooruV01PostExtractor,
    "#sha1_url"    : "3f9cd2fadf78869b90bc5422f27b48f1af0e0909",
    "#sha1_content": "159e60b92d05597bd1bb63510c2c3e4a4bada1dc",
},

)
