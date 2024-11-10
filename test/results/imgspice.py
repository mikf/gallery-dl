# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://imgspice.com/q1taxkhxprrn/58410038_cal022jsp_308191001.jpg.html",
    "#category": ("imagehost", "imgspice", "image"),
    "#class"   : imagehosts.ImgspiceImageExtractor,
    "#urls"         : "https://img30.imgspice.com/i/03792/q1taxkhxprrn.jpg",
    "#sha1_content" : "f1de8e58a7c2ef747a206a38f96c5623b8a83edc",

    "extension": "jpg",
    "filename" : "58410038_cal022jsp_308191001",
    "token"    : "q1taxkhxprrn",
},

)
