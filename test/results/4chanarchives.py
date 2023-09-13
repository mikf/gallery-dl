# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.4chanarchives")
_4chanarchives = getattr(gallery_dl.extractor, "4chanarchives")


__tests__ = (
{
    "#url"     : "https://4chanarchives.com/board/c/thread/2707110",
    "#category": ("", "4chanarchives", "thread"),
    "#class"   : _4chanarchives._4chanarchivesThreadExtractor,
    "#pattern" : r"https://i\.imgur\.com/(0wLGseE|qbByWDc)\.jpg",
    "#count"   : 2,

    "board" : "c",
    "com"   : str,
    "name"  : "Anonymous",
    "no"    : int,
    "thread": "2707110",
    "time"  : r"re:2016-07-1\d \d\d:\d\d:\d\d",
    "title" : "Ren Kagami from 'Oyako Neburi'",
},

{
    "#url"     : "https://4chanarchives.com/board/c/",
    "#category": ("", "4chanarchives", "board"),
    "#class"   : _4chanarchives._4chanarchivesBoardExtractor,
    "#pattern" : _4chanarchives._4chanarchivesThreadExtractor.pattern,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://4chanarchives.com/board/c",
    "#category": ("", "4chanarchives", "board"),
    "#class"   : _4chanarchives._4chanarchivesBoardExtractor,
},

{
    "#url"     : "https://4chanarchives.com/board/c/10",
    "#category": ("", "4chanarchives", "board"),
    "#class"   : _4chanarchives._4chanarchivesBoardExtractor,
},

)
