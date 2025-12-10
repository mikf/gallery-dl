# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fitnakedgirls


__tests__ = (
{
    "#url"     : "https://fitnakedgirls.com/photos/gallery/sparksgowild-nude/",
    "#comment" : "newer template with wp-block-image figures",
    "#category": ("", "fitnakedgirls", "gallery"),
    "#class"   : fitnakedgirls.FitnakedgirlsGalleryExtractor,
    "#pattern" : r"https://fitnakedgirls\.com/photos/wp-content/uploads/\d+/\d+/.+\.(jpg|mp4)",
    "#count"   : range(60, 70),

    "gallery_id"  : 419511,
    "gallery_slug": "sparksgowild-nude",
    "model"       : "SparksGoWild",
    "title"       : "SparksGoWild",
},

{
    "#url"     : "https://fitnakedgirls.com/photos/gallery/mikayla-demaiter-mikayla_demaiter-nude-8-photos-2/",
    "#comment" : "older template with size-large img tags",
    "#category": ("", "fitnakedgirls", "gallery"),
    "#class"   : fitnakedgirls.FitnakedgirlsGalleryExtractor,
    "#pattern" : r"https://fitnakedgirls\.com/photos/wp-content/uploads/\d+/\d+/.+\.jpg",
    "#count"   : 8,

    "gallery_id"  : 329550,
    "gallery_slug": "mikayla-demaiter-mikayla_demaiter-nude-8-photos-2",
    "model"       : "Mikayla Demaiter (mikayla_demaiter)",
    "title"       : "Mikayla Demaiter (mikayla_demaiter)",
},

{
    "#url"     : "https://fitnakedgirls.com/photos/gallery/category/fit-naked-girls/",
    "#category": ("", "fitnakedgirls", "category"),
    "#class"   : fitnakedgirls.FitnakedgirlsCategoryExtractor,
    "#pattern" : fitnakedgirls.FitnakedgirlsGalleryExtractor.pattern,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://fitnakedgirls.com/photos/gallery/tag/blonde/",
    "#category": ("", "fitnakedgirls", "tag"),
    "#class"   : fitnakedgirls.FitnakedgirlsTagExtractor,
    "#pattern" : fitnakedgirls.FitnakedgirlsGalleryExtractor.pattern,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://fitnakedgirls.com/videos/2025/08/arikytsya-gym-sybian-riding-ppv-video/",
    "#category": ("", "fitnakedgirls", "video"),
    "#class"   : fitnakedgirls.FitnakedgirlsVideoExtractor,
    "#pattern" : r"https://fitnakedgirls\.com/videos/wp-content/uploads/.+\.mp4",
    "#count"   : 1,

    "video_id": 456559,
    "slug"    : "arikytsya-gym-sybian-riding-ppv-video",
    "title"   : "Arikytsya Gym Sybian Riding PPV Video",
},

{
    "#url"     : "https://fitnakedgirls.com/fitblog/haven-schulz-2/",
    "#category": ("", "fitnakedgirls", "blog"),
    "#class"   : fitnakedgirls.FitnakedgirlsBlogExtractor,
    "#pattern" : r"https://fitnakedgirls\.com/fitblog/wp-content/uploads/.+\.(jpg|png)",
    "#count"   : 10,

    "post_id": 165409,
    "slug"   : "haven-schulz-2",
    "title"  : "Haven Schulz",
},

)
