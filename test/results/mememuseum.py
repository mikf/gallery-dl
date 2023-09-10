# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://meme.museum/post/list/animated/1",
    "#category": ("shimmie2", "mememuseum", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://meme\.museum/_images/\w+/\d+%20-%20",
    "#count"   : ">= 30",
},

{
    "#url"     : "https://meme.museum/post/view/10243",
    "#category": ("shimmie2", "mememuseum", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#pattern"     : r"https://meme\.museum/_images/105febebcd5ca791ee332adc49971f78/10243%20-%20g%20beard%20open_source%20richard_stallman%20stallman%20tagme%20text\.jpg",
    "#sha1_content": "45565f3f141fc960a8ae1168b80e718a494c52d2",

    "extension"  : "jpg",
    "file_url"   : "https://meme.museum/_images/105febebcd5ca791ee332adc49971f78/10243%20-%20g%20beard%20open_source%20richard_stallman%20stallman%20tagme%20text.jpg",
    "filename"   : "10243 - g beard open_source richard_stallman stallman tagme text",
    "height"     : 451,
    "id"         : 10243,
    "md5"        : "105febebcd5ca791ee332adc49971f78",
    "size"       : 0,
    "subcategory": "post",
    "tags"       : "/g/ beard open_source richard_stallman stallman tagme text",
    "width"      : 480,
},

)
