# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://rbt.asia/g/thread/61487650/",
    "#category": ("foolfuuka", "rbt", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "fadd274b25150a1bdf03a40c58db320fa3b617c4",
},

{
    "#url"     : "https://archive.rebeccablacktech.com/g/thread/61487650/",
    "#category": ("foolfuuka", "rbt", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "fadd274b25150a1bdf03a40c58db320fa3b617c4",
},

{
    "#url"     : "https://rbt.asia/g/",
    "#category": ("foolfuuka", "rbt", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://rbt.asia/_/search/text/test/",
    "#category": ("foolfuuka", "rbt", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://rbt.asia/g/gallery/8",
    "#category": ("foolfuuka", "rbt", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
