# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hotleakstv
from gallery_dl import exception

__tests__ = (
{
    "#url"     : "https://hotleaks.tv/kaiyakawaii/photo/1617145",
    "#category": ("", "hotleakstv", "post"),
    "#class"   : hotleakstv.HotleakstvPostExtractor,
    "#pattern" : r"https://hotleaks\.tv/storage/images/3625/1617145/fefdd5988dfcf6b98cc9e11616018868\.jpg",

    "id"       : 1617145,
    "creator"  : "kaiyakawaii",
    "type"     : "photo",
    "filename" : "fefdd5988dfcf6b98cc9e11616018868",
    "extension": "jpg",
},

{
    "#url"     : "https://hotleaks.tv/lilmochidoll/video/1625538",
    "#category": ("", "hotleakstv", "post"),
    "#class"   : hotleakstv.HotleakstvPostExtractor,
    "#pattern" : r"ytdl:https://cdn12-leak\.camhdxx\.com/1661/1625538/index\.m3u8",

    "id"       : 1625538,
    "creator"  : "lilmochidoll",
    "type"     : "video",
    "filename" : "index",
    "extension": "mp4",
},

{
    "#url"     : "https://hotleaks.tv/kaiyakawaii",
    "#category": ("", "hotleakstv", "creator"),
    "#class"   : hotleakstv.HotleakstvCreatorExtractor,
    "#range"   : "1-200",
    "#count"   : 200,
},

{
    "#url"     : "https://hotleaks.tv/stellaviolet",
    "#category": ("", "hotleakstv", "creator"),
    "#class"   : hotleakstv.HotleakstvCreatorExtractor,
    "#count"   : "> 600",
},

{
    "#url"     : "https://hotleaks.tv/doesnotexist",
    "#category": ("", "hotleakstv", "creator"),
    "#class"   : hotleakstv.HotleakstvCreatorExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://hotleaks.tv/photos",
    "#category": ("", "hotleakstv", "category"),
    "#class"   : hotleakstv.HotleakstvCategoryExtractor,
    "#pattern" : hotleakstv.HotleakstvPostExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://hotleaks.tv/videos",
    "#category": ("", "hotleakstv", "category"),
    "#class"   : hotleakstv.HotleakstvCategoryExtractor,
},

{
    "#url"     : "https://hotleaks.tv/creators",
    "#category": ("", "hotleakstv", "category"),
    "#class"   : hotleakstv.HotleakstvCategoryExtractor,
    "#pattern" : hotleakstv.HotleakstvCreatorExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://hotleaks.tv/hot",
    "#category": ("", "hotleakstv", "category"),
    "#class"   : hotleakstv.HotleakstvCategoryExtractor,
},

{
    "#url"     : "https://hotleaks.tv/search?search=gallery-dl",
    "#category": ("", "hotleakstv", "search"),
    "#class"   : hotleakstv.HotleakstvSearchExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://hotleaks.tv/search?search=hannah",
    "#category": ("", "hotleakstv", "search"),
    "#class"   : hotleakstv.HotleakstvSearchExtractor,
    "#count"   : "> 30",
},

)
