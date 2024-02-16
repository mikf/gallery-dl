# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.2chan")
_2chan = getattr(gallery_dl.extractor, "2chan")


__tests__ = (
{
    "#url"     : "https://dec.2chan.net/70/res/17222.htm",
    "#category": ("", "2chan", "thread"),
    "#class"   : _2chan._2chanThreadExtractor,
    "#pattern" : r"https://dec\.2chan\.net/70/src/\d{13}\.jpg",
    "#count"   : ">= 2",

    "board"     : "70",
    "board_name": "新板提案",
    "com"       : str,
    "fsize"     : r"re:\d+",
    "name"      : "名無し",
    "no"        : r"re:17\d\d\d",
    "now"       : r"re:2[34]/../..\(.\)..:..:..",
    "post"      : "無題",
    "server"    : "dec",
    "thread"    : "17222",
    "tim"       : r"re:^\d{13}$",
    "time"      : r"re:^\d{10}$",
    "title"     : "画像会話板",
},

)
