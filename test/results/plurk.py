# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import plurk


__tests__ = (
{
    "#url"     : "https://www.plurk.com/plurkapi",
    "#category": ("", "plurk", "timeline"),
    "#class"   : plurk.PlurkTimelineExtractor,
    "#pattern" : "https?://.+",
    "#count"   : ">= 23",
},

{
    "#url"     : "https://www.plurk.com/p/i701j1",
    "#category": ("", "plurk", "post"),
    "#class"   : plurk.PlurkPostExtractor,
    "#count"   : 3,
    "#sha1_url": "2115f208564591b8748525c2807a84596aaaaa5f",
},

{
    "#url"     : "https://www.plurk.com/p/i701j1",
    "#category": ("", "plurk", "post"),
    "#class"   : plurk.PlurkPostExtractor,
    "#options" : {"comments": True},
    "#count"   : ">= 210",
},

)
