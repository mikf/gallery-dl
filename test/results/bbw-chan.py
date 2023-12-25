# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lynxchan


__tests__ = (
{
    "#url"     : "https://bbw-chan.link/bbwdraw/res/499.html",
    "#category": ("lynxchan", "bbw-chan", "thread"),
    "#class"   : lynxchan.LynxchanThreadExtractor,
    "#pattern" : r"https://bbw-chan\.link/\.media/[0-9a-f]{64}(\.\w+)?$",
    "#count"   : ">= 352",
},

{
    "#url"     : "https://bbw-chan.nl/bbwdraw/res/489.html",
    "#category": ("lynxchan", "bbw-chan", "thread"),
    "#class"   : lynxchan.LynxchanThreadExtractor,
},

{
    "#url"     : "https://bbw-chan.link/bbwdraw/",
    "#category": ("lynxchan", "bbw-chan", "board"),
    "#class"   : lynxchan.LynxchanBoardExtractor,
    "#pattern" : lynxchan.LynxchanThreadExtractor.pattern,
    "#count"   : ">= 148",
},

{
    "#url"     : "https://bbw-chan.nl/bbwdraw/2.html",
    "#category": ("lynxchan", "bbw-chan", "board"),
    "#class"   : lynxchan.LynxchanBoardExtractor,
},

)
