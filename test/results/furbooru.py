# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import philomena


__tests__ = (
{
    "#url"     : "https://furbooru.org/images/1",
    "#category": ("philomena", "furbooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
    "#sha1_content": "9eaa1e1b32fa0f16520912257dbefaff238d5fd2",
},

{
    "#url"     : "https://furbooru.org/search?q=cute",
    "#category": ("philomena", "furbooru", "search"),
    "#class"   : philomena.PhilomenaSearchExtractor,
    "#range"   : "40-60",
    "#count"   : 21,
},

{
    "#url"     : "https://furbooru.org/galleries/27",
    "#category": ("philomena", "furbooru", "gallery"),
    "#class"   : philomena.PhilomenaGalleryExtractor,
    "#count"   : ">= 13",
},

)
