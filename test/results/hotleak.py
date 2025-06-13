# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hotleak
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://hotleak.vip/kaiyakawaii/photo/1617145",
    "#category": ("", "hotleak", "post"),
    "#class"   : hotleak.HotleakPostExtractor,
    "#results" : "https://image-cdn.hotleak.vip/storage/images/e98/18ad68/18ad68.webp",

    "id"       : 1617145,
    "creator"  : "kaiyakawaii",
    "type"     : "photo",
    "filename" : "18ad68",
    "extension": "webp",
},

{
    "#url"     : "https://hotleak.vip/lilmochidoll/video/1625538",
    "#category": ("", "hotleak", "post"),
    "#class"   : hotleak.HotleakPostExtractor,
    "#pattern" : r"ytdl:https://cdn\d+-leak\.camhdxx\.com/.+,\d+/1661/1625538/index\.m3u8",

    "id"       : 1625538,
    "creator"  : "lilmochidoll",
    "type"     : "video",
    "filename" : "index",
    "extension": "mp4",
},

{
    "#url"     : "https://hotleak.vip/kaiyakawaii",
    "#category": ("", "hotleak", "creator"),
    "#class"   : hotleak.HotleakCreatorExtractor,
    "#range"   : "1-200",
    "#count"   : 200,
},

{
    "#url"     : "https://hotleak.vip/stellaviolet",
    "#category": ("", "hotleak", "creator"),
    "#class"   : hotleak.HotleakCreatorExtractor,
    "#count"   : "> 600",
},

{
    "#url"     : "https://hotleak.vip/doesnotexist",
    "#category": ("", "hotleak", "creator"),
    "#class"   : hotleak.HotleakCreatorExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://hotleak.vip/photos",
    "#category": ("", "hotleak", "category"),
    "#class"   : hotleak.HotleakCategoryExtractor,
    "#pattern" : hotleak.HotleakPostExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://hotleak.vip/videos",
    "#category": ("", "hotleak", "category"),
    "#class"   : hotleak.HotleakCategoryExtractor,
},

{
    "#url"     : "https://hotleak.vip/creators",
    "#category": ("", "hotleak", "category"),
    "#class"   : hotleak.HotleakCategoryExtractor,
    "#pattern" : hotleak.HotleakCreatorExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://hotleak.vip/hot",
    "#category": ("", "hotleak", "category"),
    "#class"   : hotleak.HotleakCategoryExtractor,
},

{
    "#url"     : "https://hotleak.vip/search?search=gallery-dl",
    "#category": ("", "hotleak", "search"),
    "#class"   : hotleak.HotleakSearchExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://hotleak.vip/search?search=hannah",
    "#category": ("", "hotleak", "search"),
    "#class"   : hotleak.HotleakSearchExtractor,
    "#count"   : "> 30",
},

)
