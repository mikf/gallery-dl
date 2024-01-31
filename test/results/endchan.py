# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lynxchan


__tests__ = (
{
    "#url"     : "https://endchan.org/yuri/res/33621.html",
    "#category": ("lynxchan", "endchan", "thread"),
    "#class"   : lynxchan.LynxchanThreadExtractor,
    "#urls"    : "https://endchan.org/.media/358c089df4be990e9f7b636e1ce83d3e-imagejpeg.jpg",
},

{
    "#url"     : "https://endchan.org/yuri/res/33621.html",
    "#category": ("lynxchan", "endchan", "thread"),
    "#class"   : lynxchan.LynxchanThreadExtractor,
},

{
    "#url"     : "https://endchan.org/yuri/",
    "#category": ("lynxchan", "endchan", "board"),
    "#class"   : lynxchan.LynxchanBoardExtractor,
    "#pattern" : lynxchan.LynxchanThreadExtractor.pattern,
    "#count"   : ">= 8",
},

{
    "#url"     : "https://endchan.org/yuri/catalog.html",
    "#category": ("lynxchan", "endchan", "board"),
    "#class"   : lynxchan.LynxchanBoardExtractor,
},

)
