# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xvideos


__tests__ = (
{
    "#url"     : "https://www.xvideos.com/profiles/pervertedcouple/photos/751031",
    "#category": ("", "xvideos", "gallery"),
    "#class"   : xvideos.XvideosGalleryExtractor,
    "#pattern" : r"https://profile-pics-cdn\d+\.xvideos-cdn\.com/[^/]+\,\d+/videos/profiles/galleries/84/ca/37/pervertedcouple/gal751031/pic_\d+_big\.jpg",
    "#count"   : 8,

    "gallery": {
        "id"   : 751031,
        "title": "Random Stuff",
        "tags" : list,
    },
    "user"   : {
        "id"         : 20245371,
        "name"       : "pervertedcouple",
        "display"    : "Pervertedcouple",
        "sex"        : "Woman",
        "description": str,
    },
},

{
    "#url"     : "https://www.xvideos.com/amateur-channels/pervertedcouple/photos/12",
    "#category": ("", "xvideos", "gallery"),
    "#class"   : xvideos.XvideosGalleryExtractor,
},

{
    "#url"     : "https://www.xvideos.com/model-channels/pervertedcouple/photos/12",
    "#category": ("", "xvideos", "gallery"),
    "#class"   : xvideos.XvideosGalleryExtractor,
},

{
    "#url"     : "https://www.xvideos.com/profiles/pervertedcouple",
    "#category": ("", "xvideos", "user"),
    "#class"   : xvideos.XvideosUserExtractor,
    "#sha1_url"     : "a413f3e60d6d3a2de79bd44fa3b7a9c03db4336e",
    "#sha1_metadata": "335a3304941ff2e666c0201e9122819b61b34adb",
},

{
    "#url"     : "https://www.xvideos.com/profiles/pervertedcouple#_tabPhotos",
    "#category": ("", "xvideos", "user"),
    "#class"   : xvideos.XvideosUserExtractor,
},

)
