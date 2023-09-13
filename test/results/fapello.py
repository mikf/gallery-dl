# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fapello
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://fapello.com/carrykey/530/",
    "#category": ("", "fapello", "post"),
    "#class"   : fapello.FapelloPostExtractor,
    "#pattern" : r"https://fapello\.com/content/c/a/carrykey/1000/carrykey_0530\.jpg",

    "model"    : "carrykey",
    "id"       : 530,
    "type"     : "photo",
    "thumbnail": "",
},

{
    "#url"     : "https://fapello.com/vladislava-661/693/",
    "#category": ("", "fapello", "post"),
    "#class"   : fapello.FapelloPostExtractor,
    "#pattern" : r"https://cdn\.fapello\.com/content/v/l/vladislava-661/1000/vladislava-661_0693\.mp4",

    "model"    : "vladislava-661",
    "id"       : 693,
    "type"     : "video",
    "thumbnail": "https://fapello.com/content/v/l/vladislava-661/1000/vladislava-661_0693.jpg",
},

{
    "#url"     : "https://fapello.com/carrykey/000/",
    "#category": ("", "fapello", "post"),
    "#class"   : fapello.FapelloPostExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://fapello.com/hyoon/",
    "#category": ("", "fapello", "model"),
    "#class"   : fapello.FapelloModelExtractor,
    "#pattern" : fapello.FapelloPostExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://fapello.com/kobaebeefboo/",
    "#category": ("", "fapello", "model"),
    "#class"   : fapello.FapelloModelExtractor,
},

{
    "#url"     : "https://fapello.com/top-likes/",
    "#category": ("", "fapello", "path"),
    "#class"   : fapello.FapelloPathExtractor,
    "#pattern" : fapello.FapelloModelExtractor.pattern,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://fapello.com/videos/",
    "#category": ("", "fapello", "path"),
    "#class"   : fapello.FapelloPathExtractor,
    "#pattern" : fapello.FapelloPostExtractor.pattern,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://fapello.com/top-followers/",
    "#category": ("", "fapello", "path"),
    "#class"   : fapello.FapelloPathExtractor,
},

{
    "#url"     : "https://fapello.com/trending/",
    "#category": ("", "fapello", "path"),
    "#class"   : fapello.FapelloPathExtractor,
},

{
    "#url"     : "https://fapello.com/popular_videos/twelve_hours/",
    "#category": ("", "fapello", "path"),
    "#class"   : fapello.FapelloPathExtractor,
},

{
    "#url"     : "https://fapello.com/popular_videos/week/",
    "#category": ("", "fapello", "path"),
    "#class"   : fapello.FapelloPathExtractor,
},

)
