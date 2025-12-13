# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.2chen")
_2chen = getattr(gallery_dl.extractor, "2chen")


__tests__ = (
{
    "#url"     : "https://sturdychan.help/tv/268929",
    "#category": ("2chen", "sturdychan", "thread"),
    "#class"   : _2chen._2chenThreadExtractor,
    "#pattern" : r"https://sturdychan\.help/assets/images/src/\w{40}\.\w+$",
    "#count"   : ">= 179",

    "board" : "tv",
    "date"  : "type:datetime",
    "hash"  : r"re:[0-9a-f]{40}",
    "name"  : "Anonymous",
    "no"    : r"re:\d+",
    "thread": "268929",
    "time"  : int,
    "title" : "「/ttg/ #118: 🇧🇷 edition」",
    "url"   : str,
},

{
    "#url"     : "https://2chen.club/tv/1",
    "#category": ("2chen", "sturdychan", "thread"),
    "#class"   : _2chen._2chenThreadExtractor,
},

{
    "#url"     : "https://2chen.moe/jp/303786",
    "#category": ("2chen", "sturdychan", "thread"),
    "#class"   : _2chen._2chenThreadExtractor,
},

{
    "#url"     : "https://sturdychan.help/co/",
    "#category": ("2chen", "sturdychan", "board"),
    "#class"   : _2chen._2chenBoardExtractor,
    "#pattern" : _2chen._2chenThreadExtractor.pattern,
},

{
    "#url"     : "https://2chen.moe/co",
    "#category": ("2chen", "sturdychan", "board"),
    "#class"   : _2chen._2chenBoardExtractor,
},

{
    "#url"     : "https://2chen.club/tv",
    "#category": ("2chen", "sturdychan", "board"),
    "#class"   : _2chen._2chenBoardExtractor,
},

{
    "#url"     : "https://2chen.moe/co/catalog",
    "#category": ("2chen", "sturdychan", "board"),
    "#class"   : _2chen._2chenBoardExtractor,
},

)
