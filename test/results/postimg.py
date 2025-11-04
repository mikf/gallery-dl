# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://postimages.org/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
    "#results" : "https://i.postimg.cc/PhJZt1Rw/test-tesuto.png?dl=1",
},

{
    "#url"     : "https://www.postimages.org/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
},

{
    "#url"     : "https://pixxxels.cc/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
},

{
    "#url"     : "https://postimg.cc/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
    "#results"      : "https://i.postimg.cc/PhJZt1Rw/test-tesuto.png?dl=1",
    "#sha1_content" : "cfaa8def53ed1a575e0c665c9d6d8cf2aac7a0ee",

    "extension": "png",
    "filename" : "test-テスト-\"&>",
    "token"    : "Wtn2b3hC",
},

{
    "#url"     : "https://postimg.cc/gallery/wxpDLgX",
    "#category": ("imagehost", "postimg", "gallery"),
    "#class"   : imagehosts.PostimgGalleryExtractor,
    "#pattern" : imagehosts.PostimgImageExtractor.pattern,
    "#count"   : 22,
},

)
