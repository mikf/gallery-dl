# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://soybooru.com/post/view/142188",
    "#category": ("shimmie2", "soybooru", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#results" : "https://soybooru.com/_images/79a229384727558c651816e4c30c9b4d/142188%20-%20SoyBooru.png",

    "extension": "png",
    "file_url" : "https://soybooru.com/_images/79a229384727558c651816e4c30c9b4d/142188%20-%20SoyBooru.png",
    "filename" : "142188 - SoyBooru",
    "height"   : 600,
    "id"       : 142188,
    "md5"      : "79a229384727558c651816e4c30c9b4d",
    "size"     : 0,
    "tags"     : "body clothes dark dark_room glasses hair ominous shadow subvariant:pol_face template variant:chudjak white_shirt white_skin",
    "width"    : 600,
},

{
    "#url"     : "https://soybooru.com/post/list/dark_room/1",
    "#category": ("shimmie2", "soybooru", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://soybooru.com/_images/\w{32}/\d+.+\.(jpe?g|png|gif|mp4|webm)",
    "#count"   : range(16, 24),

    "extension"  : str,
    "file_url"   : str,
    "filename"   : str,
    "height"     : int,
    "id"         : int,
    "md5"        : "hash:md5",
    "search_tags": "dark_room",
    "size"       : int,
    "tags"       : str,
    "width"      : int,
},

)
