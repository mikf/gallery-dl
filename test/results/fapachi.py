# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fapachi


__tests__ = (
{
    "#url"     : "https://fapachi.com/sonson/media/0082",
    "#comment" : "NSFW",
    "#category": ("", "fapachi", "post"),
    "#class"   : fapachi.FapachiPostExtractor,
    "#pattern" : r"https://fapachi\.com/models/s/o/sonson/1/full/sonson_0082\.jpeg",

    "user": "sonson",
    "id"  : "0082",
},

{
    "#url"     : "https://fapachi.com/ferxiita/media/0159",
    "#comment" : "NSFW",
    "#category": ("", "fapachi", "post"),
    "#class"   : fapachi.FapachiPostExtractor,
},

{
    "#url"     : "https://fapachi.com/sonson",
    "#category": ("", "fapachi", "user"),
    "#class"   : fapachi.FapachiUserExtractor,
    "#pattern" : fapachi.FapachiPostExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://fapachi.com/ferxiita/page/3",
    "#category": ("", "fapachi", "user"),
    "#class"   : fapachi.FapachiUserExtractor,
},

)
