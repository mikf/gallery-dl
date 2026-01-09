# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import furaffinity


__tests__ = (
{
    "#url"     : "https://www.furaffinity.net/gallery/mirlinthloth/",
    "#category": ("", "furaffinity", "gallery"),
    "#class"   : furaffinity.FuraffinityGalleryExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/mirlinthloth/\d+/\d+.\w+\.\w+",
    "#range"   : "45-50",
    "#count"   : 6,
},

{
    "#url"     : "https://www.furaffinity.net/gallery/markrun15/folder/173240/Inanimate/?",
    "#category": ("", "furaffinity", "folder"),
    "#class"   : furaffinity.FuraffinityFolderExtractor,
    "#range"   : "46-50",
    "#urla"    : (
        "https://d.furaffinity.net/art/markrun15/1598704240/1598704240.markrun15_20200829_dusknoir_flat3.jpg",
        "https://d.furaffinity.net/art/markrun15/1598704109/1598704109.markrun15_20200829_dusknoir_flat1.jpg",
        "https://d.furaffinity.net/art/markrun15/1588674514/1588674514.markrun15_20200504_cubemorgana.jpg",
        "https://d.furaffinity.net/art/markrun15/1588501280/1588501280.markrun15_20200427_inanimate_animal3.jpg",
        "https://d.furaffinity.net/art/markrun15/1588501161/1588501161.markrun15_20200427_inanimate_animal.jpg",
    ),

    "folder_id"  : "173240",
    "folder_name": "Inanimate",
},

{
    "#url"     : "https://www.furaffinity.net/scraps/mirlinthloth/",
    "#category": ("", "furaffinity", "scraps"),
    "#class"   : furaffinity.FuraffinityScrapsExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/[^/]+(/stories)?/\d+/\d+.\w+.",
    "#count"   : ">= 3",
},

{
    "#url"     : "https://www.furaffinity.net/favorites/mirlinthloth/",
    "#category": ("", "furaffinity", "favorite"),
    "#class"   : furaffinity.FuraffinityFavoriteExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/[^/]+/\d+/\d+.\w+\.\w+",
    "#range"   : "45-50",
    "#count"   : 6,

    "favorite_id": int,
},

{
    "#url"     : "https://www.furaffinity.net/favorites/mirlinthloth/46682246/next?",
    "#comment" : "custom start location",
    "#class"   : furaffinity.FuraffinityFavoriteExtractor,
    "#auth"    : False,
    "#range"   : "1-3",
    "#results" : (
        "https://d.furaffinity.net/art/kacey/1263424668/1263424668.kacey_mine.jpg",
        "https://d.furaffinity.net/art/leomon32/1254250660/1254250660.leomon32_high_in_the_sky.jpg",
        "https://d.furaffinity.net/art/firefoxzero/1262442028/1262442028.firefoxzero_resolute_model_4.png",
    ),
},

{
    "#url"     : "https://www.furaffinity.net/search/?q=cute",
    "#category": ("", "furaffinity", "search"),
    "#class"   : furaffinity.FuraffinitySearchExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/[^/]+/\d+/\d+.\w+\.\w+",
    "#range"   : "45-50",
    "#count"   : 6,
},

{
    "#url"     : "https://www.furaffinity.net/search/?q=leaf&range=1day",
    "#comment" : "first page of search results (#2402)",
    "#category": ("", "furaffinity", "search"),
    "#class"   : furaffinity.FuraffinitySearchExtractor,
    "#range"   : "1-3",
    "#count"   : 3,
},

{
    "#url"     : "https://www.furaffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
    "#pattern" : r"https://d\d*\.f(uraffinity|acdn)\.net/(download/)?art/mirlinthloth/music/1488278723/1480267446.mirlinthloth_dj_fennmink_-_bude_s_4_ever\.mp3",

    "artist"     : "mirlinthloth",
    "artist_url" : "mirlinthloth",
    "date"       : "dt:2016-11-27 17:24:06",
    "description": "A Song made playing the game Cosmic DJ.",
    "extension"  : "mp3",
    "filename"   : r"re:\d+\.\w+_dj_fennmink_-_bude_s_4_ever",
    "id"         : 21835115,
    "tags"       : list,
    "title"      : "Bude's 4 Ever",
    "url"        : r"re:https://d\d?\.f(uraffinity|acdn)\.net/art",
    "user"       : "mirlinthloth",
    "views"      : int,
    "favorites"  : int,
    "comments"   : int,
    "rating"     : "General",
    "fa_category": "Music",
    "theme"      : "All",
    "species"    : "Unspecified / Any",
    "gender"     : "Any",
    "width"      : 120,
    "height"     : 120,
    "scraps"     : False,
},

{
    "#url"     : "https://www.furaffinity.net/view/42166511/",
    "#comment" : "'external' option (#1492)",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
    "#options" : {"external": True},
    "#pattern" : r"https://d\d*\.f(uraffinity|acdn)\.net/|http://www\.postybirb\.com",
    "#count"   : 2,
},

{
    "#url"     : "https://www.furaffinity.net/view/45331225/",
    "#comment" : "no tags (#2277)",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,

    "artist"     : "Kota_Remminders",
    "artist_url" : "kotaremminders",
    "date"       : "dt:2022-01-03 17:49:33",
    "fa_category": "Adoptables",
    "filename"   : "1641232173.kotaremminders_chidopts1",
    "gender"     : "Any",
    "height"     : 905,
    "id"         : 45331225,
    "rating"     : "General",
    "species"    : "Unspecified / Any",
    "tags"       : [],
    "theme"      : "All",
    "title"      : "REMINDER",
    "width"      : 1280,
},

{
    "#url"     : "https://www.furaffinity.net/view/22964019/",
    "#comment" : "get thumbnails for posts (#1284)",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,

    "artist"      : "Dwale",
    "artist_url"  : "dwale",
    "date"        : "dt:2017-03-21 14:21:29",
    "fa_category" : "Poetry",
    "filename"    : "1490106089.dwale_poem_for_children",
    "folders"     : [],
    "height"      : 50,
    "id"          : 22964019,
    "rating"      : "General",
    "title"       : "Poem for Children Wishing to Summon Evil Spirits",
    "thumbnail"   : "https://t.furaffinity.net/22964019@600-1490106089.jpg",
    "width"       : 50,
},

{
    "#url"     : "https://www.furaffinity.net/view/34260156/",
    "#comment" : "list gallery folders for image",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,

    "artist"      : "dbd",
    "artist_url"  : "dbd",
    "date"        : "dt:2019-12-17 22:52:01",
    "fa_category" : "All",
    "filename"    : "1576623121.dbd_patreoncustom-wdg13-web",
    "folders"     : ["By Year - 2019",
                     "Custom Character Folder - All Custom Characters",
                     "Custom Character Folder - Other Ungulates",
                     "Custom Character Folder - Female",
                     "Custom Character Folder - Patreon Supported Custom Characters"],
    "id"          : 34260156,
    "rating"      : "General",
    "title"       : "Patreon Custom Deer",
    "thumbnail"   : "https://t.furaffinity.net/34260156@600-1576623121.jpg",
    "width"       : 488,
    "height"      : 900,
    "scraps"      : False,
},

{
    "#url"     : "https://www.furaffinity.net/view/4919026/",
    "#comment" : "'scraps' metadata (#7015)",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
    "#auth"    : False,

    "id"         : 4919026,
    "scraps"     : True,
    "title"      : "Loth Color Test",
    "rating"     : "General",
    "theme"      : "Fantasy",
    "species"    : "Dragon (Other)",
    "gender"     : "Multiple characters",
    "width"      : 600,
    "height"     : 777,
    "user"       : "mirlinthloth",
    "date"       : "dt:2010-12-10 01:47:23",
    "description": "I think this is the first coloring for Loth that I did, I loved the goofy expression so I kept it.",
    "folders": [
        "Mirlinth Loth",
        "Akiric Works",
    ],
},

{
    "#url"     : "https://www.furaffinity.net/view/46163989/",
    "#comment" : "display names (#7115 #7123)",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,

    "artist"    : "Pickra the magical feline",
    "artist_url": "pickra",
    "user"      : "pickra",
},

{
    "#url"     : "https://www.furaffinity.net/view/57587562",
    "#comment" : "login required",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://furaffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://fxfuraffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://xfuraffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://fxraffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://sfw.furaffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://www.furaffinity.net/full/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://www.furaffinity.net/user/mirlinthloth/",
    "#category": ("", "furaffinity", "user"),
    "#class"   : furaffinity.FuraffinityUserExtractor,
    "#pattern" : "/gallery/mirlinthloth/$",
},

{
    "#url"     : "https://www.furaffinity.net/user/mirlinthloth/",
    "#category": ("", "furaffinity", "user"),
    "#class"   : furaffinity.FuraffinityUserExtractor,
    "#options" : {"include": "all"},
    "#pattern" : "/(gallery|scraps|favorites)/mirlinthloth/$",
    "#count"   : 3,
},

{
    "#url"     : "https://www.furaffinity.net/watchlist/by/mirlinthloth/",
    "#category": ("", "furaffinity", "following"),
    "#class"   : furaffinity.FuraffinityFollowingExtractor,
    "#pattern" : furaffinity.FuraffinityUserExtractor.pattern,
    "#range"   : "176-225",
    "#count"   : 50,
},

{
    "#url"     : "https://www.furaffinity.net/msg/submissions",
    "#category": ("", "furaffinity", "submissions"),
    "#class"   : furaffinity.FuraffinitySubmissionsExtractor,
    "#auth"    : True,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/mirlinthloth/\d+/\d+.\w+\.\w+",
    "#range"   : "45-50",
    "#count"   : 6,
},

{
    "#url"     : "https://www.furaffinity.net/msg/submissions/new~56789000@48/",
    "#category": ("", "furaffinity", "submissions"),
    "#class"   : furaffinity.FuraffinitySubmissionsExtractor,
    "#auth"    : True,
},

)
