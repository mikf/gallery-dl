# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://archive.palanq.win/c/thread/4209598/",
    "#category": ("foolfuuka", "palanq", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "1f9b5570d228f1f2991c827a6631030bc0e5933c",
},

{
    "#url"     : "https://archive.palanq.win/c/",
    "#category": ("foolfuuka", "palanq", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://archive.palanq.win/_/search/text/test/",
    "#category": ("foolfuuka", "palanq", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://archive.palanq.win/c/gallery",
    "#category": ("foolfuuka", "palanq", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
