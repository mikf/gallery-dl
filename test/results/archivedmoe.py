# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://archived.moe/gd/thread/309639/",
    "#category": ("foolfuuka", "archivedmoe", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url"    : "fdd533840e2d535abd162c02d6dfadbc12e2dcd8",
    "#sha1_content": "c27e2a7be3bc989b5dd859f7789cc854db3f5573",
},

{
    "#url"     : "https://archived.moe/a/thread/159767162/",
    "#category": ("foolfuuka", "archivedmoe", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "ffec05a1a1b906b5ca85992513671c9155ee9e87",
},

{
    "#url"     : "https://archived.moe/b/thread/912594917/",
    "#comment" : "broken thebarchive .webm URLs (#5116)",
    "#category": ("foolfuuka", "archivedmoe", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#results" : (
        "https://thebarchive.com/b/full_image/1705625299234839.gif",
        "https://thebarchive.com/b/full_image/1705625431133806.web",
        "https://thebarchive.com/b/full_image/1705626190307840.web",
    ),
},

{
    "#url"     : "https://archived.moe/a/thread/279540316/",
    "#comment" : "filename/timestamp fixup for redirect URL (#7652)",
    "#category": ("foolfuuka", "archivedmoe", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#results" : (
        "http://desuarchive.org/a/full_image/1749537017533.jpg",
    ),
},

{
    "#url"     : "https://archived.moe/gd/",
    "#category": ("foolfuuka", "archivedmoe", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://archived.moe/_/search/text/test/",
    "#category": ("foolfuuka", "archivedmoe", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://archived.moe/gd/gallery/2",
    "#category": ("foolfuuka", "archivedmoe", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
