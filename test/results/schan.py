# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.2chen")
_2chen = getattr(gallery_dl.extractor, "2chen")


__tests__ = (
{
    "#url"     : "https://schan.help/tv/757",
    "#category": ("2chen", "schan", "thread"),
    "#class"   : _2chen._2chenThreadExtractor,
    "#pattern" : r"https://schan\.help/assets/images/src/\w{40}\.\w+$",
    "#count"   : ">= 179",

    "board" : "tv",
    "date"  : "type:datetime",
    "hash"  : "",
    "name"  : "Anonymous",
    "no"    : r"re:\d+",
    "thread": "757",
    "time"  : int,
    "title" : "「/ttg/ #1: The Future of Schan」",
    "url"   : str,
},

{
    "#url"     : "https://schan.help/tv/",
    "#category": ("2chen", "schan", "board"),
    "#class"   : _2chen._2chenBoardExtractor,
    "#pattern" : _2chen._2chenThreadExtractor.pattern,
},

)
