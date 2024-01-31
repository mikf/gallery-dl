# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://sizechangebooru.com/index.php?q=/post/list/drawing/1",
    "#category": ("shimmie2", "giantessbooru", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://sizechangebooru\.com/index\.php\?q=/image/\d+\.jpg",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://giantessbooru.com/index.php?q=/post/list/drawing/1",
    "#category": ("shimmie2", "giantessbooru", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
},

{
    "#url"     : "https://giantessbooru.com/post/list/drawing/1",
    "#category": ("shimmie2", "giantessbooru", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
},

{
    "#url"     : "https://sizechangebooru.com/index.php?q=/post/view/41",
    "#category": ("shimmie2", "giantessbooru", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#urls"        : "https://sizechangebooru.com/index.php?q=/image/41.jpg",
    "#sha1_content": "79115ed309d1f4e82e7bead6948760e889139c91",

    "extension": "jpg",
    "file_url" : "https://sizechangebooru.com/index.php?q=/image/41.jpg",
    "filename" : "41",
    "height"   : 0,
    "id"       : 41,
    "md5"      : "",
    "size"     : 0,
    "tags"     : "anime bare_midriff color drawing gentle giantess karbo looking_at_tinies negeyari outdoors smiling snake_girl white_hair",
    "width"    : 1387,
},

{
    "#url"     : "https://giantessbooru.com/index.php?q=/post/view/41",
    "#category": ("shimmie2", "giantessbooru", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
},

{
    "#url"     : "https://giantessbooru.com/post/view/41",
    "#category": ("shimmie2", "giantessbooru", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
},

)
