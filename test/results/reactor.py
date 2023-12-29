# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import reactor


__tests__ = (
{
    "#url"     : "http://reactor.cc/tag/gif",
    "#category": ("reactor", "reactor", "tag"),
    "#class"   : reactor.ReactorTagExtractor,
},

{
    "#url"     : "http://reactor.cc/search?q=Art",
    "#category": ("reactor", "reactor", "search"),
    "#class"   : reactor.ReactorSearchExtractor,
},

{
    "#url"     : "http://reactor.cc/user/Dioklet",
    "#category": ("reactor", "reactor", "user"),
    "#class"   : reactor.ReactorUserExtractor,
},

{
    "#url"     : "http://reactor.cc/post/4999736",
    "#category": ("reactor", "reactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#sha1_url": "dfc74d150d7267384d8c229c4b82aa210755daa0",
},

)
