# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vichan


__tests__ = (
{
    "#url"     : "https://8kun.top/test/res/65248.html",
    "#category": ("vichan", "8kun", "thread"),
    "#class"   : vichan.VichanThreadExtractor,
    "#pattern" : r"https://media\.128ducks\.com/file_store/\w{64}\.\w+",
    "#count"   : ">= 8",
},

{
    "#url"     : "https://8kun.top/v/index.html",
    "#category": ("vichan", "8kun", "board"),
    "#class"   : vichan.VichanBoardExtractor,
    "#pattern" : vichan.VichanThreadExtractor.pattern,
    "#count"   : ">= 100",
},

{
    "#url"     : "https://8kun.top/v/2.html",
    "#category": ("vichan", "8kun", "board"),
    "#class"   : vichan.VichanBoardExtractor,
},

{
    "#url"     : "https://8kun.top/v/index.html?PageSpeed=noscript",
    "#category": ("vichan", "8kun", "board"),
    "#class"   : vichan.VichanBoardExtractor,
},

)
