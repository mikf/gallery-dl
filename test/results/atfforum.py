# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo


__tests__ = (
{
    "#url"     : "https://www.allthefallen.moe/forum/index.php?threads/final-fantasy-xiv.57090/post-21765744",
    "#category": ("xenforo", "atfforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://allthefallen.moe/forum/index.php?attachments/ffxiv_dx11-2025-04-28-09-16-54-png.4368606/",

    "count"       : 1,
    "extension"   : "png",
    "filename"    : "ffxiv_dx11 2025-04-28 09-16-54",
    "id"          : 4368606,
    "num"         : 1,
    "num_external": 0,
    "num_internal": 1,
    "type"        : "inline",
    "post"        : {
        "attachments": "",
        "author"     : "mayumiXIV",
        "author_id"  : "965353",
        "author_url" : "https://allthefallen.moe/forum/index.php?members/mayumixiv.965353/",
        "count"      : 1,
        "date"       : "dt:2025-04-28 15:28:24",
        "id"         : "21765744",
        "content"    : str
    },
    "thread"      : {
        "author"    : "Kupowo",
        "author_id" : "649590",
        "author_url": "https://allthefallen.moe/forum/index.php?members/kupowo.649590/",
        "date"      : "dt:2023-12-25 21:15:53",
        "id"        : "57090",
        "section"   : "Gaming",
        "title"     : "Final Fantasy XIV",
        "url"       : "https://allthefallen.moe/forum/index.php?threads/final-fantasy-xiv.57090/",
        "posts"     : range(210, 280),
        "views"     : range(7300, 9000),
        "tags"      : [
            "ff14",
            "final fantasy 14",
            "final fantasy xiv",
        ],
    },
},

{
    "#url"     : "https://www.allthefallen.moe/forum/index.php?threads/final-fantasy-xiv.57090/#post-21765744",
    "#category": ("xenforo", "atfforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
},

{
    "#url"     : "https://www.allthefallen.moe/forum/index.php?threads/shoujo-ramune-episode-1-decensored-by-deepcreampy.17050/#post-19803487",
    "#comment" : "incomplete video URL (#8786)",
    "#category": ("xenforo", "atfforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://allthefallen.moe/forum/data/video/1094/1094367-e46ad8636dee0d4488db56d3770919cc.mp4",
},

{
    "#url"     : "https://www.allthefallen.moe/forum/index.php?threads/final-fantasy-xiv.57090/",
    "#category": ("xenforo", "atfforum", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
    "#auth"    : True,
    "#count"   : range(50, 90),

    "count"       : int,
    "num"         : int,
    "num_external": int,
    "num_internal": int,
    "type"        : {"inline", "external"},
    "post"        : {
        "attachments": str,
        "author"     : str,
        "author_id"  : r"re:\d",
        "author_url" : r"re:https://allthefallen.moe/forum/index.php\?members/.+",
        "count"      : range(0, 9),
        "date"       : "type:datetime",
        "id"         : r"re:\d+",
        "content"    : str,
    },
    "thread"      : {
        "author"    : "Kupowo",
        "author_id" : "649590",
        "author_url": "https://allthefallen.moe/forum/index.php?members/kupowo.649590/",
        "date"      : "dt:2023-12-25 21:15:53",
        "id"        : "57090",
        "section"   : "Gaming",
        "title"     : "Final Fantasy XIV",
        "url"       : "https://allthefallen.moe/forum/index.php?threads/final-fantasy-xiv.57090/",
        "posts"     : range(210, 280),
        "views"     : range(7300, 9000),
        "tags"      : [
            "ff14",
            "final fantasy 14",
            "final fantasy xiv",
        ],
    },
},

{
    "#url"     : "https://www.allthefallen.moe/forum/index.php?forums/announcements.16/",
    "#category": ("xenforo", "atfforum", "forum"),
    "#class"   : xenforo.XenforoForumExtractor,
    "#pattern" : xenforo.XenforoThreadExtractor.pattern,
    "#auth"    : True,
    "#count"   : range(100, 200),
},

{
    "#url"     : "https://allthefallen.moe/forum/index.php?media/1737485564664-png.224260/",
    "#category": ("xenforo", "atfforum", "media-item"),
    "#class"   : xenforo.XenforoMediaItemExtractor,
    "#options" : {"metadata": False},
    "#results" : "https://allthefallen.moe/forum/index.php?media/1737485564664-png.224260/full",

    "extension": "png",
    "filename" : "1737485564664",
    "id"       : "224260",
},

{
    "#url"     : "https://allthefallen.moe/forum/index.php?media/users/peters.150992/",
    "#category": ("xenforo", "atfforum", "media-user"),
    "#class"   : xenforo.XenforoMediaUserExtractor,
    "#options" : {"metadata": False},
    "#auth"    : True,
    "#results" : (
        "https://allthefallen.moe/forum/index.php?media/eden-invitation-jpg.254624/full",
        "https://allthefallen.moe/forum/index.php?media/1737485564664-png.224260/full",
        "https://allthefallen.moe/forum/index.php?media/laughing-cat-emoji-png.243825/full",
    ),
},

{
    "#url"     : "https://allthefallen.moe/forum/index.php?members/peters.150992/#xfmgMedia",
    "#category": ("xenforo", "atfforum", "media-user"),
    "#class"   : xenforo.XenforoMediaUserExtractor,
},

{
    "#url"     : "https://www.allthefallen.moe/forum/index.php?media/categories/translations.2/",
    "#category": ("xenforo", "atfforum", "media-category"),
    "#class"   : xenforo.XenforoMediaCategoryExtractor,
},

)
