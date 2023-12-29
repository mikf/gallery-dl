# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vichan


__tests__ = (
{
    "#url"     : "https://wikieat.club/cel/res/25321.html",
    "#category": ("vichan", "wikieat", "thread"),
    "#class"   : vichan.VichanThreadExtractor,
    "#pattern" : r"https://wikieat\.club/cel/src/\d+(-\d)?\.\w+",
    "#count"   : ">= 200",
},

{
    "#url"     : "https://wikieat.club/cel/index.html",
    "#category": ("vichan", "wikieat", "board"),
    "#class"   : vichan.VichanBoardExtractor,
    "#pattern" : vichan.VichanThreadExtractor.pattern,
    "#count"   : ">= 100",
},

{
    "#url"     : "https://wikieat.club/cel/catalog.html",
    "#category": ("vichan", "wikieat", "board"),
    "#class"   : vichan.VichanBoardExtractor,
},

{
    "#url"     : "https://wikieat.club/cel/2.html",
    "#category": ("vichan", "wikieat", "board"),
    "#class"   : vichan.VichanBoardExtractor,
},

)
