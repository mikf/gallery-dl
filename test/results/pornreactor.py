# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import reactor


__tests__ = (
{
    "#url"     : "http://pornreactor.cc/tag/RiceGnat",
    "#category": ("reactor", "pornreactor", "tag"),
    "#class"   : reactor.ReactorTagExtractor,
    "#range"   : "1-25",
    "#count"   : ">= 25",
},

{
    "#url"     : "http://fapreactor.com/tag/RiceGnat",
    "#category": ("reactor", "pornreactor", "tag"),
    "#class"   : reactor.ReactorTagExtractor,
},

{
    "#url"     : "http://pornreactor.cc/search?q=ecchi+hentai",
    "#category": ("reactor", "pornreactor", "search"),
    "#class"   : reactor.ReactorSearchExtractor,
},

{
    "#url"     : "http://fapreactor.com/search/ecchi+hentai",
    "#category": ("reactor", "pornreactor", "search"),
    "#class"   : reactor.ReactorSearchExtractor,
},

{
    "#url"     : "http://pornreactor.cc/user/Disillusion",
    "#category": ("reactor", "pornreactor", "user"),
    "#class"   : reactor.ReactorUserExtractor,
    "#range"   : "1-25",
    "#count"   : ">= 20",
},

{
    "#url"     : "http://fapreactor.com/user/Disillusion",
    "#category": ("reactor", "pornreactor", "user"),
    "#class"   : reactor.ReactorUserExtractor,
},

{
    "#url"     : "http://pornreactor.cc/post/863166",
    "#category": ("reactor", "pornreactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#sha1_url"    : "a09fb0577489e1f9564c25d0ad576f81b19c2ef3",
    "#sha1_content": "ec6b0568bfb1803648744077da082d14de844340",
},

{
    "#url"     : "http://fapreactor.com/post/863166",
    "#category": ("reactor", "pornreactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#sha1_url": "2a956ce0c90e8bc47b4392db4fa25ad1342f3e54",
},

)
