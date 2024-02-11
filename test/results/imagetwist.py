# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://imagetwist.com/f1i2s4vhvbrq/test.png",
    "#category": ("imagehost", "imagetwist", "image"),
    "#class"   : imagehosts.ImagetwistImageExtractor,
    "#sha1_url"     : "8d5e168c0bee30211f821c6f3b2116e419d42671",
    "#sha1_metadata": "d1060a4c2e3b73b83044e20681712c0ffdd6cfef",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",
},

{
    "#url"     : "https://www.imagetwist.com/f1i2s4vhvbrq/test.png",
    "#category": ("imagehost", "imagetwist", "image"),
    "#class"   : imagehosts.ImagetwistImageExtractor,
},

{
    "#url"     : "https://phun.imagetwist.com/f1i2s4vhvbrq/test.png",
    "#category": ("imagehost", "imagetwist", "image"),
    "#class"   : imagehosts.ImagetwistImageExtractor,
},

{
    "#url"     : "https://imagehaha.com/f1i2s4vhvbrq/test.png",
    "#category": ("imagehost", "imagetwist", "image"),
    "#class"   : imagehosts.ImagetwistImageExtractor,
},

{
    "#url"     : "https://www.imagehaha.com/f1i2s4vhvbrq/test.png",
    "#category": ("imagehost", "imagetwist", "image"),
    "#class"   : imagehosts.ImagetwistImageExtractor,
},

{
    "#url"     : "https://imagetwist.com/p/gdldev/747223/digits",
    "#category": ("imagehost", "imagetwist", "gallery"),
    "#class"   : imagehosts.ImagetwistGalleryExtractor,
    "#urls"    : (
        "https://imagetwist.com/j6eu91sbl9bs",
        "https://imagetwist.com/vx4oh119izyr",
        "https://imagetwist.com/n3td3a6vzzed",
        "https://imagetwist.com/8uz6lmg31nmc",
    ),
},

)
