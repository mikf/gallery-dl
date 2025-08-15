# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import leakgallery
FILE_PATTERN = r"https://cdn.leakgallery.com/content(-videos|\d+)?/[\w.-]+\.\w+"


__tests__ = (
{
    "#url"    : "https://leakgallery.com/sophieraiin/12240",
    "#class"  : leakgallery.LeakgalleryPostExtractor,
    "#results": "https://cdn.leakgallery.com/content-videos/watermark_745_sophieraiin_241.mp4",

    "id"     : "12240",
    "creator": "sophieraiin",
},

{
    "#url"    : "https://leakgallery.com/sophieraiin",
    "#class"  : leakgallery.LeakgalleryUserExtractor,
    "#pattern": r"https://cdn.leakgallery.com/content3/(compressed_)?watermark_[0-9a-f]+_sophieraiin_\w+\.(jpg|png|mp4|mov)",
    "#range"  : "1-100",
    "#count"  : 100,

    "creator": "sophieraiin",
},

{
    "#url"    : "https://leakgallery.com/trending-medias/Week",
    "#class"  : leakgallery.LeakgalleryTrendingExtractor,
    "#pattern": FILE_PATTERN,
    "#range"  : "1-100",
    "#count"  : 100,
},

{
    "#url"    : "https://leakgallery.com/most-liked",
    "#class"  : leakgallery.LeakgalleryMostlikedExtractor,
    "#pattern": FILE_PATTERN,
    "#range"  : "1-100",
    "#count"  : 100,
},

)
