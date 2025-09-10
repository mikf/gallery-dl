# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vichan


__tests__ = (
{
    "#url"     : "https://boards.guro.cx/art/res/7184.html#q7184",
    "#category": ("vichan", "gurochan", "thread"),
    "#class"   : vichan.VichanThreadExtractor,
    "#pattern" : r"https://boards\.guro\.cx/art/src/\d+\.\w+",
    "#count"   : range(50, 80),
},

{
    "#url"     : "https://boards.guro.cx/art/",
    "#category": ("vichan", "gurochan", "board"),
    "#class"   : vichan.VichanBoardExtractor,
    "#pattern" : vichan.VichanThreadExtractor.pattern,
    "#count"   : range(500, 800),
},

)
