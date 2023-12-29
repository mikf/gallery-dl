# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://boards.fireden.net/sci/thread/11264294/",
    "#category": ("foolfuuka", "fireden", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "61cab625c95584a12a30049d054931d64f8d20aa",
},

{
    "#url"     : "https://boards.fireden.net/sci/",
    "#category": ("foolfuuka", "fireden", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://boards.fireden.net/_/search/text/test/",
    "#category": ("foolfuuka", "fireden", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://boards.fireden.net/sci/gallery/6",
    "#category": ("foolfuuka", "fireden", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
