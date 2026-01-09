# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://imagetwist.com/f1i2s4vhvbrq/test.png",
    "#category": ("imagehost", "imagetwist", "image"),
    "#class"   : imagehosts.ImagetwistImageExtractor,
    "#sha1_url"     : "8d5e168c0bee30211f821c6f3b2116e419d42671",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",

    "filename" : "test",
    "extension": "png",
    "token"    : "f1i2s4vhvbrq",
    "post_url" : "https://imagetwist.com/f1i2s4vhvbrq",
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
    "#url"     : "https://imagetwist.com/tynhxt4ay9rl/9g09tq0e2i1b.jpg",
    "#comment" : "'Image not found' (#8415)",
    "#category": ("imagehost", "imagetwist", "image"),
    "#class"   : imagehosts.ImagetwistImageExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://imagetwist.com/p/gdldev/747223/digits",
    "#category": ("imagehost", "imagetwist", "gallery"),
    "#class"   : imagehosts.ImagetwistGalleryExtractor,
    "#results" : (
        "https://imagetwist.com/j6eu91sbl9bs",
        "https://imagetwist.com/vx4oh119izyr",
        "https://imagetwist.com/n3td3a6vzzed",
        "https://imagetwist.com/8uz6lmg31nmc",
    ),

    "gallery_id"   : "747223",
    "gallery_title": "digits",
},

{
    "#url"     : "https://imagetwist.com/p/gdldev/806105/multi",
    "#comment" : "multiple pages (#8826)",
    "#category": ("imagehost", "imagetwist", "gallery"),
    "#class"   : imagehosts.ImagetwistGalleryExtractor,
    "#pattern" : imagehosts.ImagetwistImageExtractor.pattern,
    "#count"   : 100,

    "gallery_id"   : "806105",
    "gallery_title": "multi",
},

{
    "#url"     : "https://imagetwist.com/?op=user_public&per_page=40&fld_id=806105&usr_login=gdldev&page=2",
    "#comment" : "'page=' URL (#8826)",
    "#category": ("imagehost", "imagetwist", "gallery"),
    "#class"   : imagehosts.ImagetwistGalleryExtractor,
    "#pattern" : imagehosts.ImagetwistImageExtractor.pattern,
    "#count"   : 60,

    "gallery_id"   : "806105",
    "gallery_title": "multi",
},

)
