# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://desuarchive.org/a/thread/159542679/",
    "#category": ("foolfuuka", "desuarchive", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url": "e7d624aded15a069194e38dc731ec23217a422fb",
},

{
    "#url"     : "https://desuarchive.org/a",
    "#category": ("foolfuuka", "desuarchive", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://desuarchive.org/a/",
    "#category": ("foolfuuka", "desuarchive", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://desuarchive.org/a/2",
    "#category": ("foolfuuka", "desuarchive", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://desuarchive.org/a/page/2",
    "#category": ("foolfuuka", "desuarchive", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
    "#pattern" : foolfuuka.FoolfuukaThreadExtractor.pattern,
    "#count"   : 10,
},

{
    "#url"     : "https://desuarchive.org/_/search/text/test/",
    "#category": ("foolfuuka", "desuarchive", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://desuarchive.org/a/gallery/5",
    "#category": ("foolfuuka", "desuarchive", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
