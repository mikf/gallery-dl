# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.2ch")
_2ch = getattr(gallery_dl.extractor, "2ch")


__tests__ = (
{
    "#url"     : "https://2ch.hk/a/res/6202876.html",
    "#category": ("", "2ch", "thread"),
    "#class"   : _2ch._2chThreadExtractor,
    "#pattern" : r"https://2ch\.hk/a/src/6202876/\d+\.\w+",
    "#count"   : range(450, 1000),

    "banned"   : 0,
    "board"    : "a",
    "closed"   : 0,
    "comment"  : str,
    "date"     : "type:datetime",
    "displayname": str,
    "email"    : str,
    "endless"  : 1,
    "extension": str,
    "filename" : str,
    "fullname" : str,
    "height"   : int,
    "lasthit"  : range(1705000000, 1900000000),
    "md5"      : r"re:[0-9a-f]{32}",
    "name"     : r"re:\d+\.\w+",
    "num"      : int,
    "number"   : range(1, 1000),
    "op"       : 0,
    "parent"   : int,
    "path"     : r"re:/a/src/6202876/\d+\.\w+",
    "post_name": str,
    "size"     : int,
    "sticky"   : 0,
    "subject"  : str,
    "thread"   : "6202876",
    "thumbnail": str,
    "tim"      : r"re:\d+",
    "timestamp": int,
    "title"    : "MP4/WEBM",
    "tn_height": int,
    "tn_width" : int,
    "trip"     : "",
    "type"     : int,
    "views"    : int,
    "width"    : int,
},

{
    "#url"     : "https://2ch.hk/a/",
    "#category": ("", "2ch", "board"),
    "#class"   : _2ch._2chBoardExtractor,
    "#pattern" : _2ch._2chThreadExtractor.pattern,
    "#count"   : range(200, 400),
},

)
