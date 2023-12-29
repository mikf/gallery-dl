# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lynxchan


__tests__ = (
{
    "#url"     : "https://kohlchan.net/a/res/4594.html",
    "#category": ("lynxchan", "kohlchan", "thread"),
    "#class"   : lynxchan.LynxchanThreadExtractor,
    "#pattern" : r"https://kohlchan\.net/\.media/[0-9a-f]{64}(\.\w+)?$",
    "#count"   : ">= 80",
},

{
    "#url"     : "https://kohlchan.net/a/",
    "#category": ("lynxchan", "kohlchan", "board"),
    "#class"   : lynxchan.LynxchanBoardExtractor,
    "#pattern" : lynxchan.LynxchanThreadExtractor.pattern,
    "#count"   : ">= 100",
},

{
    "#url"     : "https://kohlchan.net/a/2.html",
    "#category": ("lynxchan", "kohlchan", "board"),
    "#class"   : lynxchan.LynxchanBoardExtractor,
},

{
    "#url"     : "https://kohlchan.net/a/catalog.html",
    "#category": ("lynxchan", "kohlchan", "board"),
    "#class"   : lynxchan.LynxchanBoardExtractor,
},

)
