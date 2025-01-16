# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import e621


__tests__ = (
{
    "#url"     : "https://e621.cc/?tags=rating:safe",
    "#category": ("E621", "e621", "frontend"),
    "#class"   : e621.E621FrontendExtractor,
    "#urls"    : "https://e621.net/posts?tags=rating:safe",
},

{
    "#url"     : "https://e621.anthro.fr/?q=rating:safe",
    "#category": ("E621", "e621", "frontend"),
    "#class"   : e621.E621FrontendExtractor,
    "#urls"    : "https://e621.net/posts?tags=rating:safe",
},

)
