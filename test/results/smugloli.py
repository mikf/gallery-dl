# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vichan


__tests__ = (
{
    "#url"     : "https://smuglo.li/a/res/1187531.html",
    "#category": ("vichan", "smugloli", "thread"),
    "#class"   : vichan.VichanThreadExtractor,
    "#pattern" : r"https://smug.+/a/src/\d+(-\d)?\.\w+",
    "#count"   : ">= 50",

    "board" : "a",
    "thread": "1187531",
    "title" : "Buta no Liver wa Kanetsu Shiro",
},

{
    "#url"     : "https://smugloli.net/a/res/1145409.html",
    "#category": ("vichan", "smugloli", "thread"),
    "#class"   : vichan.VichanThreadExtractor,
},

{
    "#url"     : "https://smuglo.li/a",
    "#category": ("vichan", "smugloli", "board"),
    "#class"   : vichan.VichanBoardExtractor,
    "#pattern" : vichan.VichanThreadExtractor.pattern,
    "#count"   : ">= 100",
},

{
    "#url"     : "https://smuglo.li/a/1.html",
    "#category": ("vichan", "smugloli", "board"),
    "#class"   : vichan.VichanBoardExtractor,
},

{
    "#url"     : "https://smugloli.net/cute/catalog.html",
    "#category": ("vichan", "smugloli", "board"),
    "#class"   : vichan.VichanBoardExtractor,
},

)
