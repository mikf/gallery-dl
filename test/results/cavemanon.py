# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://booru.cavemanon.xyz/index.php?q=post/list/Amber/1",
    "#category": ("shimmie2", "cavemanon", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://booru\.cavemanon\.xyz/index\.php\?q=image/\d+\.\w+",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://booru.cavemanon.xyz/post/list/Amber/1",
    "#category": ("shimmie2", "cavemanon", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
},

{
    "#url"     : "https://booru.cavemanon.xyz/index.php?q=post/view/8335",
    "#category": ("shimmie2", "cavemanon", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#pattern"     : r"https://booru\.cavemanon\.xyz/index\.php\?q=image/8335\.png",
    "#sha1_content": "7158f7e4abbbf143bad5835eb93dbe4d68c1d4ab",

    "extension": "png",
    "file_url" : "https://booru.cavemanon.xyz/index.php?q=image/8335.png",
    "filename" : "8335",
    "height"   : 460,
    "id"       : 8335,
    "md5"      : "",
    "size"     : 0,
    "tags"     : "Color Fang Food Pterodactyl discord_emote transparent",
    "width"    : 459,
},

)
