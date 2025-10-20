# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nijie


__tests__ = (
{
    "#url"     : "https://horne.red/members.php?id=58000",
    "#category": ("Nijie", "horne", "user"),
    "#class"   : nijie.NijieUserExtractor,
    "#results" : (
        "https://horne.red/members_illust.php?id=58000",
        "https://horne.red/members_dojin.php?id=58000",
    ),
},

{
    "#url"     : "https://horne.red/members_illust.php?id=58000",
    "#category": ("Nijie", "horne", "illustration"),
    "#class"   : nijie.NijieIllustrationExtractor,
    "#pattern" : r"https://pic\.nijie\.net/__s4__/[0-9a-f]{184}\.png",
    "#range"   : "1-20",
    "#count"   : 20,

    "artist_id"  : 58000,
    "artist_name": "のえるわ",
    "date"       : "type:datetime",
    "description": str,
    "image_id"   : int,
    "num"        : int,
    "tags"       : list,
    "title"      : str,
    "url"        : str,
    "user_id"    : 58000,
    "user_name"  : "のえるわ",
},

{
    "#url"     : "https://horne.red/members_dojin.php?id=58000",
    "#category": ("Nijie", "horne", "doujin"),
    "#class"   : nijie.NijieDoujinExtractor,
},

{
    "#url"     : "https://horne.red/user_like_illust_view.php?id=58000",
    "#category": ("Nijie", "horne", "favorite"),
    "#class"   : nijie.NijieFavoriteExtractor,
    "#range"   : "1-5",
    "#count"   : 5,

    "user_id"  : 58000,
    "user_name": "のえるわ",
},

{
    "#url"     : "https://horne.red/history_nuita.php?id=58000",
    "#category": ("Nijie", "horne", "nuita"),
    "#class"   : nijie.NijieNuitaExtractor,
},

{
    "#url"     : "https://horne.red/like_user_view.php",
    "#category": ("Nijie", "horne", "feed"),
    "#class"   : nijie.NijieFeedExtractor,
},

{
    "#url"     : "https://horne.red/like_my.php",
    "#category": ("Nijie", "horne", "followed"),
    "#class"   : nijie.NijieFollowedExtractor,
},

{
    "#url"     : "https://horne.red/view.php?id=8708",
    "#category": ("Nijie", "horne", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#results" : "https://pic.nijie.net/__s4__/d7e18cb679f35b388dc8b0b9f2edb178078469b8970ee099cd573a577bc3a84cf33a04581f20b1cbed44bcd86147348cccdf7ded3b974bfb5b2711c2afb27c67834a22bd7411aa43895c9f480bbbed7373d345c24ac55e36018ad065.png",

    "artist_id"  : 58000,
    "artist_name": "のえるわ",
    "count"      : 1,
    "date"       : "dt:2018-01-29 14:25:39",
    "description": "前回とシチュがまるかぶり　\r\n竿野郎は塗るのだるかった",
    "extension"  : "png",
    "filename"   : "d7e18cb679f35b388dc8b0b9f2edb178078469b8970ee099cd573a577bc3a84cf33a04581f20b1cbed44bcd86147348cccdf7ded3b974bfb5b2711c2afb27c67834a22bd7411aa43895c9f480bbbed7373d345c24ac55e36018ad065",
    "image_id"   : 8708,
    "num"        : 0,
    "tags"       : [
        "男の娘",
        "オリキャラ",
        "うちのこ",
    ],
    "title"      : "うちのこえっち",
    "url"        : "https://pic.nijie.net/__s4__/d7e18cb679f35b388dc8b0b9f2edb178078469b8970ee099cd573a577bc3a84cf33a04581f20b1cbed44bcd86147348cccdf7ded3b974bfb5b2711c2afb27c67834a22bd7411aa43895c9f480bbbed7373d345c24ac55e36018ad065.png",
    "user_id"    : 58000,
    "user_name"  : "のえるわ",
},

{
    "#url"     : "https://horne.red/view.php?id=8716",
    "#category": ("Nijie", "horne", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#results" : (
        "https://pic.nijie.net/__s4__/d7b784b573f850628fcae5b4f7ede679085af22dba0caf6bb91622438289ddce9312ab6f2886b8d8ef104f8eb5908d57cc309ec0239464add9f9d8d17d83c39d92c680b083f107d63c68eef29938ebc937699fd50d51b1128404cc6e.png",
        "https://pic.nijie.net/__s4__/d7b9dae222f25e388a9debb4ade7eb79b87af28c9650b1babe514902eb854bbd8cb295b379d5480ea83cad78fbc843b146785ba59f1279fa77eb14e33ca66778474afb5063ba36d9d527fa31f780fbf396b27bd9901b0e3565efce08.png",
        "https://pic.nijie.net/__s4__/d7b889b276fb5a36dacde5bef7e8ea225e06c9904f18be00035c96721dd1ac6ab7217be29f8c6f58626aa9839835185f08474efd3822a3e298c74b9f2b3d0fc1cd5400b97b74512b0800eabbdcf8d4094be666ea3b6305a436cadd10.png",
        "https://pic.nijie.net/__s4__/d7b6d9e173fc59368199ebbef6b9e728aea39dd452c9e7d83d78465e787922b5e3194ba54e58bbf753c33de2b3c9adf063b77b92e56a0b0c28c72e90d9f1d857562b87b2a836c083b5ff85709ebd9e93dd19774fa5a8d624133d4eda.png",
    ),

    "artist_id"  : 58000,
    "artist_name": "のえるわ",
    "count"      : 4,
    "date"       : "dt:2018-02-04 14:47:24",
    "description": "ノエル「そんなことしなくても、言ってくれたら咥えるのに・・・♡」",
    "image_id"   : 8716,
    "num"        : range(0, 3),
    "tags"       : [
        "男の娘",
        "フェラ",
        "オリキャラ",
        "うちのこ",
    ],
    "title"      : "ノエル「いまどきそんな、恵方巻ネタなんてやらなくても・・・」",
    "user_id"    : 58000,
    "user_name"  : "のえるわ",
},

)
