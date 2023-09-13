# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://arch.b4k.co/meta/thread/196/",
    "#category": ("foolfuuka", "b4k", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "d309713d2f838797096b3e9cb44fe514a9c9d07a",
},

{
    "#url"     : "https://arch.b4k.co/meta/",
    "#category": ("foolfuuka", "b4k", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://arch.b4k.co/meta/gallery/",
    "#category": ("foolfuuka", "b4k", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
