# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import postype


__tests__ = (
{
    "#url"     : "https://www.postype.com/@miragestar602/post/21436111",
    "#category": ("", "postype", "post"),
    "#class"   : postype.PostypePostExtractor,
    "#count"   : 1,
    "#pattern" : r"https://d2ufj6gm1gtdrc\.cloudfront\.net/.+",
},

{
    "#url"     : "https://www.postype.com/@miragestar602",
    "#category": ("", "postype", "channel"),
    "#class"   : postype.PostypeChannelExtractor,
    "#pattern" : r"https://www\.postype\.com/@miragestar602/post/\d+",
    "#range"   : "1-3",
    "#count"   : 3,
},
)
