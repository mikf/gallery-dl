# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.2chan")
_2chan = getattr(gallery_dl.extractor, "2chan")


__tests__ = (
{
    "#url"     : "https://dec.2chan.net/70/res/14565.htm",
    "#category": ("", "2chan", "thread"),
    "#class"   : _2chan._2chanThreadExtractor,
    "#pattern" : r"https://dec\.2chan\.net/70/src/\d{13}\.jpg",
    "#count"   : ">= 3",

    "board"     : "70",
    "board_name": "新板提案",
    "com"       : str,
    "fsize"     : r"re:\d+",
    "name"      : "名無し",
    "no"        : r"re:1[45]\d\d\d",
    "now"       : r"re:22/../..\(.\)..:..:..",
    "post"      : "無題",
    "server"    : "dec",
    "thread"    : "14565",
    "tim"       : r"re:^\d{13}$",
    "time"      : r"re:^\d{10}$",
    "title"     : "ﾋﾛｱｶ板",
},

)
