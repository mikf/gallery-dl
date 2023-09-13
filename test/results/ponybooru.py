# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import philomena


__tests__ = (
{
    "#url"     : "https://ponybooru.org/images/1",
    "#category": ("philomena", "ponybooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
    "#sha1_content": "bca26f58fafd791fe07adcd2a28efd7751824605",
},

{
    "#url"     : "https://www.ponybooru.org/images/1",
    "#category": ("philomena", "ponybooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
},

{
    "#url"     : "https://ponybooru.org/search?q=cute",
    "#category": ("philomena", "ponybooru", "search"),
    "#class"   : philomena.PhilomenaSearchExtractor,
    "#range"   : "40-60",
    "#count"   : 21,
},

{
    "#url"     : "https://ponybooru.org/galleries/27",
    "#category": ("philomena", "ponybooru", "gallery"),
    "#class"   : philomena.PhilomenaGalleryExtractor,
    "#count"   : ">= 24",
},

)
