# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import jschan


__tests__ = (
{
    "#url"     : "https://94chan.org/art/thread/25.html",
    "#category": ("jschan", "94chan", "thread"),
    "#class"   : jschan.JschanThreadExtractor,
    "#pattern" : r"https://94chan.org/file/[0-9a-f]{64}(\.\w+)?",
    "#count"   : ">= 15",
},

{
    "#url"     : "https://94chan.org/art/",
    "#category": ("jschan", "94chan", "board"),
    "#class"   : jschan.JschanBoardExtractor,
    "#pattern" : jschan.JschanThreadExtractor.pattern,
    "#count"   : ">= 30",
},

{
    "#url"     : "https://94chan.org/art/2.html",
    "#category": ("jschan", "94chan", "board"),
    "#class"   : jschan.JschanBoardExtractor,
},

{
    "#url"     : "https://94chan.org/art/catalog.html",
    "#category": ("jschan", "94chan", "board"),
    "#class"   : jschan.JschanBoardExtractor,
},

{
    "#url"     : "https://94chan.org/art/index.html",
    "#category": ("jschan", "94chan", "board"),
    "#class"   : jschan.JschanBoardExtractor,
},

)
