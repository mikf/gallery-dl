# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://tentaclerape.net/post/list/comic/1",
    "#category": ("shimmie2", "tentaclerape", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://tentaclerape\.net/_images/[0-9a-f]{32}/\d+",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://tentaclerape.net/post/view/10",
    "#category": ("shimmie2", "tentaclerape", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#pattern"     : r"https://tentaclerape\.net/\./index\.php\?q=/image/10\.jpg",
    "#sha1_content": "d0fd8f0f6517a76cb5e23ba09f3844950bf2c516",

    "extension"  : "jpg",
    "file_url"   : "https://tentaclerape.net/./index.php?q=/image/10.jpg",
    "filename"   : "10",
    "height"     : 427,
    "id"         : 10,
    "md5"        : "945db71eeccaef82ce44b77564260c0b",
    "size"       : 0,
    "subcategory": "post",
    "tags"       : "Deviant_Art Pet Tentacle artist_sche blonde_hair blouse boots green_eyes highheels leash miniskirt octopus schoolgirl white_skin willing",
    "width"      : 300,
},

{
    "#url"     : "https://tentaclerape.net/post/view/91267",
    "#comment" : "video",
    "#category": ("shimmie2", "tentaclerape", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#pattern" : r"https://tentaclerape\.net/\./index\.php\?q=/image/91267\.mp4",
},

)
