# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import reactor


__tests__ = (
{
    "#url"     : "http://anime.reactor.cc/tag/Anime+Art",
    "#category": ("reactor", "anime.reactor", "tag"),
    "#class"   : reactor.ReactorTagExtractor,
},

{
    "#url"     : "http://anime.reactor.cc/user/Shuster",
    "#category": ("reactor", "anime.reactor", "user"),
    "#class"   : reactor.ReactorUserExtractor,
},

{
    "#url"     : "http://anime.reactor.cc/post/3576250",
    "#category": ("reactor", "anime.reactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
},

)
