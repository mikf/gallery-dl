# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mixdrop


__tests__ = (
{
    "#url"     : "https://m1xdrop.com/f/k0mmklw8axe09e",
    "#category": ("", "mixdrop", "file"),
    "#class"   : mixdrop.MixdropFileExtractor,
    "#pattern" : r"https://s-delivery\d+\.mxcontent\.net/v\d/k0mmklw8axe09e\.mp4",
    "#count"   : 1,

    "fid"      : "k0mmklw8axe09e",
    "title"    : "Leeds United vs Arsenal - 31012026",
    "poster"   : r"re:https://s-delivery\d+\.mxcontent.net/thumbs/k0mmklw8axe09e_5x5\.jpg",
    "filename" : "9ae814bc8aaacd419119cb1e8393c29c",
    "extension": "mp4",
},

{
    "#url"     : "https://mixdrop.ag/e/k0mmklw8axe09e",
    "#category": ("", "mixdrop", "file"),
    "#class"   : mixdrop.MixdropFileExtractor,
},

)
