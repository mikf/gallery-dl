# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://vidya.pics/post/list/kirby/1",
    "#category": ("shimmie2", "vidyapics", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://vidya.pics/_images/[0-9a-f]{32}/\d+",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://vidya.pics/post/view/108820",
    "#category": ("shimmie2", "vidyapics", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#pattern"     : r"https://vidya\.pics/_images/277ecdb90285bfa6e0c4cd46d9515b11/108820.+\.png",
    "#sha1_content": "7d2fe9327759c231ff17f6e341df749b70b191ce",

    "extension": "png",
    "file_url" : "https://vidya.pics/_images/277ecdb90285bfa6e0c4cd46d9515b11/108820%20-%201boy%20artist%3Aunknown%20flag%20kirby%20kirby_%28series%29.png",
    "filename" : "108820 - 1boy artist:unknown flag kirby kirby_(series)",
    "height"   : 700,
    "id"       : 108820,
    "md5"      : "277ecdb90285bfa6e0c4cd46d9515b11",
    "size"     : 0,
    "tags"     : "1boy artist:unknown flag kirby kirby_(series",
    "width"    : 700,
},

)
