# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import myhentaigallery


__tests__ = (
{
    "#url"     : "https://myhentaigallery.com/g/16247",
    "#category": ("", "myhentaigallery", "gallery"),
    "#class"   : myhentaigallery.MyhentaigalleryGalleryExtractor,
    "#pattern" : r"https://(cdn|images)\.myhentaicomics\.com/m\w\w/images/[^/]+/original/\d+\.jpg",

    "artist"    : list,
    "count"     : 11,
    "gallery_id": 16247,
    "group"     : list,
    "parodies"  : list,
    "tags"      : ["Giantess"],
    "title"     : "Attack Of The 50ft Woman 1",
},

{
    "#url"     : "https://myhentaigallery.com/gallery/thumbnails/16247",
    "#category": ("", "myhentaigallery", "gallery"),
    "#class"   : myhentaigallery.MyhentaigalleryGalleryExtractor,
},

{
    "#url"     : "https://myhentaigallery.com/gallery/show/16247/1",
    "#category": ("", "myhentaigallery", "gallery"),
    "#class"   : myhentaigallery.MyhentaigalleryGalleryExtractor,
},

)
