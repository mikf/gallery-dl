# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import sizebooru


__tests__ = (
{
    "#url"     : "https://sizebooru.com/Details/283342",
    "#class"   : sizebooru.SizebooruPostExtractor,
    "#results" : "https://sizebooru.com/Picture/283342",
    "#sha1_content": "ae8bcbe95d58ba8ed4f33fe017088c9ec0f09515",

    "id"           : 283342,
    "filename"     : "283342",
    "extension"    : "jpg",
    "file_url"     : "https://sizebooru.com/Picture/283342",
},

{
    "#url"     : "https://sizebooru.com/Details/283342",
    "#class"   : sizebooru.SizebooruPostExtractor,
    "#options" : {"metadata": True},
    "#results" : "https://sizebooru.com/Picture/283342",
    "#sha1_content": "ae8bcbe95d58ba8ed4f33fe017088c9ec0f09515",

    "approver"     : "Mr_Red",
    "artist"       : None,
    "date"         : "dt:2025-07-30 00:00:00",
    "date_approved": "dt:2025-08-01 00:00:00",
    "extension"    : "jpg",
    "file_url"     : "https://sizebooru.com/Picture/283342",
    "filename"     : "Gnlib9eaMAAXtfQ",
    "id"           : 283342,
    "source"       : "https://x.com/kashmimo/status/1907664168381255942",
    "uploader"     : "Shadow_Blaze_23",
    "views"        : range(200, 900),
    "favorite"     : [
        "GTSfan295",
        "Zephyr",
        "HeroDjango",
    ],
    "tags"         : [
        "drawing",
        "giantess",
        "pokemon",
        "blushing",
        "black_hair",
        "color",
        "long_hair",
        "sweat",
        "parody",
        "shrunken_man",
        "hat",
        "orange_hair",
        "looking_at_tiny",
        "leaf_(pokemon)",
        "kashmimo",
    ],
},

{
    "#url"     : "https://sizebooru.com/Details/2",
    "#class"   : sizebooru.SizebooruPostExtractor,
    "#options" : {"metadata": True},
    "#results" : "https://sizebooru.com/Picture/2",

    "approver"     : "Giantessbooru",
    "artist"       : None,
    "date"         : "dt:2010-11-26 00:00:00",
    "date_approved": "dt:2010-11-26 00:00:00",
    "extension"    : "jpg",
    "file_url"     : "https://sizebooru.com/Picture/2",
    "filename"     : "10000 - tagme",
    "id"           : 2,
    "source"       : None,
    "uploader"     : "Giantess-7of9",
    "views"        : range(40, 200),
    "favorite"     : list,
    "tags"         : [
        "breasts",
        "gentle",
        "nude",
        "black_hair",
        "long_hair",
        "brunette",
        "hand",
        "shrunken_man",
        "indoors",
        "digital_render",
    ],
},

{
    "#url"     : "https://sizebooru.com/Details/283318",
    "#class"   : sizebooru.SizebooruPostExtractor,
    "#options" : {"metadata": True},
    "#results" : "https://sizebooru.com/Picture/283318",

    "approver"     : "Mr_Red",
    "artist"       : "megamaliit",
    "date"         : "dt:2025-07-26 00:00:00",
    "date_approved": "dt:2025-07-26 00:00:00",
    "extension"    : "png",
    "file_url"     : "https://sizebooru.com/Picture/283318",
    "filename"     : "big babes of bed rock",
    "id"           : 283318,
    "source"       : "https://www.deviantart.com/megamaliit/art/Big-Babes-of-Bed-Rock-AT-845335093",
    "uploader"     : "Mr_Red",
    "views"        : int,
    "favorite"     : list,
    "tags"         : list,
},

{
    "#url"     : "https://sizebooru.com/Search/parody",
    "#category": ("booru", "sizebooru", "tag"),
    "#class"   : sizebooru.SizebooruTagExtractor,
    "#pattern" : r"https://sizebooru\.com/Picture/\d+",
    "#count"   : range(200, 300),

    "id"         : int,
    "filename"   : r"re:\d+",
    "extension"  : {"jpg", "png"},
    "file_url"   : r"re:https://stizebooru.com/Picture/\d+",
    "search_tags": "parody",
},

{
    "#url"     : "https://sizebooru.com/Galleries/List/7",
    "#category": ("booru", "sizebooru", "gallery"),
    "#class"   : sizebooru.SizebooruGalleryExtractor,
    "#pattern" : r"https://sizebooru\.com/Picture/\d+",
    "#count"   : 103,

    "gallery_id"  : 7,
    "gallery_name": "lilipucien's work",
},

{
    "#url"     : "https://sizebooru.com/Profile/Uploads/hueyriley",
    "#category": ("booru", "sizebooru", "user"),
    "#class"   : sizebooru.SizebooruUserExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://sizebooru.com/Profile/Uploads/GtsXxx",
    "#category": ("booru", "sizebooru", "user"),
    "#class"   : sizebooru.SizebooruUserExtractor,
    "#pattern" : r"https://sizebooru\.com/Picture/\d+",
    "#count"   : 256,

    "user"     : "GtsXxx",
},

{
    "#url"     : "https://sizebooru.com/Profile/Favorites/GtsXxx",
    "#category": ("booru", "sizebooru", "favorite"),
    "#class"   : sizebooru.SizebooruFavoriteExtractor,
    "#results" : (
        "https://sizebooru.com/Picture/266778",
        "https://sizebooru.com/Picture/266385",
        "https://sizebooru.com/Picture/266243",
        "https://sizebooru.com/Picture/265039",
    ),

    "user"     : "GtsXxx",
},

)
