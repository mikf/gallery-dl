# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imgth


__tests__ = (
{
    "#url"     : "https://imgth.com/gallery/37/wallpaper-anime",
    "#category": ("", "imgth", "gallery"),
    "#class"   : imgth.ImgthGalleryExtractor,
    "#pattern" : r"https://imgth\.com/images/2009/11/25/wallpaper-anime_\w+\.jpg",
    "#sha1_url": "4ae1d281ca2b48952cf5cca57e9914402ad72748",

    "count"     : 12,
    "date"      : "dt:2009-11-25 18:21:00",
    "extension" : "jpg",
    "filename"  : r"re:wallpaper-anime_\w+",
    "gallery_id": 37,
    "num"       : int,
    "title"     : "Wallpaper anime",
    "user"      : "celebrities",
},

{
    "#url"     : "https://www.imgth.com/gallery/37/wallpaper-anime",
    "#category": ("", "imgth", "gallery"),
    "#class"   : imgth.ImgthGalleryExtractor,
},

)
