# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nijie
import datetime


__tests__ = (
{
    "#url"     : "https://horne.red/members.php?id=58000",
    "#category": ("Nijie", "horne", "user"),
    "#class"   : nijie.NijieUserExtractor,
    "#urls"    : (
        "https://horne.red/members_illust.php?id=58000",
        "https://horne.red/members_dojin.php?id=58000",
    ),
},

{
    "#url"     : "https://horne.red/members_illust.php?id=58000",
    "#category": ("Nijie", "horne", "illustration"),
    "#class"   : nijie.NijieIllustrationExtractor,
    "#pattern" : r"https://pic\.nijie\.net/\d+/horne/\w+/\d+/\d+/illust/\d+_\d+_[0-9a-f]+_[0-9a-f]+\.png",
    "#range"   : "1-20",
    "#count"   : 20,

    "artist_id"  : 58000,
    "artist_name": "のえるわ",
    "date"       : datetime.datetime,
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
    "#urls"    : "https://pic.nijie.net/07/horne/18/00/58000/illust/0_0_c8f715a8f3d53943_db6231.png",

    "artist_id"  : 58000,
    "artist_name": "のえるわ",
    "count"      : 1,
    "date"       : "dt:2018-01-29 14:25:39",
    "description": "前回とシチュがまるかぶり　\r\n竿野郎は塗るのだるかった",
    "extension"  : "png",
    "filename"   : "0_0_c8f715a8f3d53943_db6231",
    "image_id"   : 8708,
    "num"        : 0,
    "tags"       : [
        "男の娘",
        "オリキャラ",
        "うちのこ",
    ],
    "title"      : "うちのこえっち",
    "url"        : "https://pic.nijie.net/07/horne/18/00/58000/illust/0_0_c8f715a8f3d53943_db6231.png",
    "user_id"    : 58000,
    "user_name"  : "のえるわ",
},

{
    "#url"     : "https://horne.red/view.php?id=8716",
    "#category": ("Nijie", "horne", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#urls"    : (
        "https://pic.nijie.net/07/horne/18/00/58000/illust/0_0_b4ffb4b6f7ec6d51_1a32c0.png",
        "https://pic.nijie.net/07/horne/18/00/58000/illust/8716_0_2690972a4f6270bb_85ed8f.png",
        "https://pic.nijie.net/07/horne/18/00/58000/illust/8716_1_09348508d8b76f36_f6cf47.png",
        "https://pic.nijie.net/08/horne/18/00/58000/illust/8716_2_5151d956d3789277_d76e75.png",
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
