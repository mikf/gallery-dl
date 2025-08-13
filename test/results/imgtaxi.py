# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://imgtaxi.com/img-61c71cea940d6.html",
    "#category": ("imagehost", "imgtaxi", "image"),
    "#class"   : imagehosts.ImgdriveImageExtractor,
    "#results" : "https://imgtaxi.com/images/big/2021/12/25/61c71cea940d5.jpg",

    "filename" : "SLn_0001",
    "extension": "jpg",
    "token"    : "61c71cea940d6",
},

)
