# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import zzup


__tests__ = (
{
    "#url"     : "https://zzup.com/content/NjM=/MetArt_20080206_viki_c_sensazioni_by_ingret/OTE=/index.html",
    "#category": ("", "zzup", "gallery"),
    "#class"   : zzup.ZzupGalleryExtractor,
    "#pattern" : r"https://zzup\.com/[^/?#]+/showimage/zzup-8769086487/image00\d\d\d-5896498214-1-9689595623/MetArt-20080206_viki_c_sensazioni_by_ingret/9879560327/zzup.com.jpg",

    "slug"  : "MetArt_20080206_viki_c_sensazioni_by_ingret",
    "title" : "MetArt 20080206 viki c sensazioni by ingret",
    "num"   : int,
    "count" : 135,
},

{
    "#url"     : "https://zzup.com/content/MTc2MDYxMw==/Courtesan/NDA=/page-1.html",
    "#category": ("", "zzup", "gallery"),
    "#class"   : zzup.ZzupGalleryExtractor,
    "#pattern" : r"https://zzup\.com/[^/?#]+/showimage/zzup-8769086487/image000\d\d-5896498214-40-9689595623/Courtesan/9879560327/zzup.com.jpg",
},

{
    "#url"     : "https://up.zzup.com/viewalbum/TE9MQUxVWlogLSBMYWxsaSAtIFdhcm0gYW5kIENvenk=/NTM0MTk=/OTgz/index.html",
    "#category": ("", "zzup", "gallery"),
    "#class"   : zzup.ZzupGalleryExtractor,
},

)
