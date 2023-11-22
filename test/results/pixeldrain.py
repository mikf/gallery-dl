# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pixeldrain


__tests__ = (
{
    "#url"     : "https://pixeldrain.com/l/r2osXHR2",
    "#category": ("", "pixeldrain", "gallery"),
    "#class"   : pixeldrain.PixeldrainGalleryExtractor,
    "#pattern" : r"https://pixeldrain\.com/api/file/\w+",

    "date" : "dt:2022-05-27 19:59:21",
    "count": 5,
    "file" : {
        "id"         : str,
        "hash_sha256": str,
        "views"      : int,
        "downloads"  : int,
        "size"       : int,
    },
},

{
    "#url"     : "https://pixeldrain.com/l/1gEJn1xc",
    "#category": ("", "pixeldrain", "gallery"),
    "#class"   : pixeldrain.PixeldrainGalleryExtractor,
    "#pattern" : r"https://pixeldrain\.com/api/file/\w+",

    "date" : "dt:2023-07-23 13:30:33",
    "count": 30,
},

)
