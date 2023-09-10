# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://archive.4plebs.org/tg/thread/54059290",
    "#category": ("foolfuuka", "4plebs", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "fd823f17b5001442b941fddcd9ec91bafedfbc79",
},

{
    "#url"     : "https://archive.4plebs.org/tg/",
    "#category": ("foolfuuka", "4plebs", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://archive.4plebs.org/_/search/text/test/",
    "#category": ("foolfuuka", "4plebs", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://archive.4plebs.org/tg/gallery/1",
    "#category": ("foolfuuka", "4plebs", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
