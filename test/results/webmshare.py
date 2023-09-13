# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import webmshare


__tests__ = (
{
    "#url"     : "https://webmshare.com/O9mWY",
    "#category": ("", "webmshare", "video"),
    "#class"   : webmshare.WebmshareVideoExtractor,

    "date"     : "dt:2022-12-04 00:00:00",
    "extension": "webm",
    "filename" : "O9mWY",
    "height"   : 568,
    "id"       : "O9mWY",
    "thumb"    : "https://s1.webmshare.com/t/O9mWY.jpg",
    "title"    : "Yeah buddy over here",
    "url"      : "https://s1.webmshare.com/O9mWY.webm",
    "views"    : int,
    "width"    : 320,
},

{
    "#url"     : "https://s1.webmshare.com/zBGAg.webm",
    "#category": ("", "webmshare", "video"),
    "#class"   : webmshare.WebmshareVideoExtractor,

    "date"  : "dt:2018-12-07 00:00:00",
    "height": 1080,
    "id"    : "zBGAg",
    "thumb" : "https://s1.webmshare.com/t/zBGAg.jpg",
    "title" : "",
    "url"   : "https://s1.webmshare.com/zBGAg.webm",
    "views" : int,
    "width" : 1920,
},

{
    "#url"     : "https://webmshare.com/play/zBGAg",
    "#category": ("", "webmshare", "video"),
    "#class"   : webmshare.WebmshareVideoExtractor,
},

{
    "#url"     : "https://webmshare.com/download-webm/zBGAg",
    "#category": ("", "webmshare", "video"),
    "#class"   : webmshare.WebmshareVideoExtractor,
},

)
