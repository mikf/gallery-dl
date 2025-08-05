# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://imgdrive.net/img-61ac0caeabf35.html",
    "#category": ("imagehost", "imgdrive", "image"),
    "#class"   : imagehosts.ImgdriveImageExtractor,
    "#results" : "https://imgdrive.net/images/big/2021/12/05/61ac0caeabf33.JPG",

    "extension": "jpg",
    "filename" : "5yl_0001",
    "token"    : "61ac0caeabf35",
},

)
