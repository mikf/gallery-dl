# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://thebarchive.com/b/thread/739772332/",
    "#category": ("foolfuuka", "thebarchive", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "e8b18001307d130d67db31740ce57c8561b5d80c",
},

{
    "#url"     : "https://thebarchive.com/b/",
    "#category": ("foolfuuka", "thebarchive", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://thebarchive.com/_/search/text/test/",
    "#category": ("foolfuuka", "thebarchive", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://thebarchive.com/b/gallery/9",
    "#category": ("foolfuuka", "thebarchive", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
