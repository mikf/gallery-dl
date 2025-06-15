# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://arch.b4k.dev/meta/thread/196/",
    "#category": ("foolfuuka", "b4k", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#results" : "https://arch.b4k.dev/media/meta/image/1481/33/14813348737492.jpg",
},

{
    "#url"     : "https://arch.b4k.co/meta/thread/196/",
    "#category": ("foolfuuka", "b4k", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#results" : "https://arch.b4k.dev/media/meta/image/1481/33/14813348737492.jpg",
},

{
    "#url"     : "https://arch.b4k.dev/meta/",
    "#category": ("foolfuuka", "b4k", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://arch.b4k.dev/meta/gallery/",
    "#category": ("foolfuuka", "b4k", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
