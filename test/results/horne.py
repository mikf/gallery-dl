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
},

{
    "#url"     : "https://horne.red/members_illust.php?id=58000",
    "#category": ("Nijie", "horne", "illustration"),
    "#class"   : nijie.NijieIllustrationExtractor,
    "#pattern" : r"https://pic\.nijie\.net/\d+/horne/\d+/\d+/\d+/illust/\d+_\d+_[0-9a-f]+_[0-9a-f]+\.png",
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
    "#url"     : "https://horne.red/view.php?id=8716",
    "#category": ("Nijie", "horne", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#count"   : 4,

    "artist_id"  : 58000,
    "artist_name": "のえるわ",
    "date"       : "dt:2018-02-04 14:47:24",
    "description": "ノエル「そんなことしなくても、言ってくれたら咥えるのに・・・♡」",
    "image_id"   : 8716,
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
