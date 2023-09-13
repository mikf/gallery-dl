# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nijie
import datetime
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://nijie.info/members.php?id=44",
    "#category": ("Nijie", "nijie", "user"),
    "#class"   : nijie.NijieUserExtractor,
},

{
    "#url"     : "https://nijie.info/members_illust.php?id=44",
    "#category": ("Nijie", "nijie", "illustration"),
    "#class"   : nijie.NijieIllustrationExtractor,
    "#sha1_url": "1553e5144df50a676f5947d02469299b401ad6c0",

    "artist_id"  : 44,
    "artist_name": "ED",
    "date"       : datetime.datetime,
    "description": str,
    "extension"  : "jpg",
    "filename"   : str,
    "image_id"   : int,
    "num"        : int,
    "tags"       : list,
    "title"      : str,
    "url"        : r"re:https://pic.nijie.net/\d+/nijie/.*jpg$",
    "user_id"    : 44,
    "user_name"  : "ED",
},

{
    "#url"     : "https://nijie.info/members_illust.php?id=43",
    "#category": ("Nijie", "nijie", "illustration"),
    "#class"   : nijie.NijieIllustrationExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://nijie.info/members_dojin.php?id=6782",
    "#category": ("Nijie", "nijie", "doujin"),
    "#class"   : nijie.NijieDoujinExtractor,
    "#count"   : ">= 18",

    "user_id"  : 6782,
    "user_name": "ジョニー＠アビオン村",
},

{
    "#url"     : "https://nijie.info/user_like_illust_view.php?id=44",
    "#category": ("Nijie", "nijie", "favorite"),
    "#class"   : nijie.NijieFavoriteExtractor,
    "#count"   : ">= 16",

    "user_id"  : 44,
    "user_name": "ED",
},

{
    "#url"     : "https://nijie.info/history_nuita.php?id=728995",
    "#category": ("Nijie", "nijie", "nuita"),
    "#class"   : nijie.NijieNuitaExtractor,
    "#range"   : "1-10",
    "#count"   : 10,

    "user_id"  : 728995,
    "user_name": "莚",
},

{
    "#url"     : "https://nijie.info/like_user_view.php",
    "#category": ("Nijie", "nijie", "feed"),
    "#class"   : nijie.NijieFeedExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://nijie.info/like_my.php",
    "#category": ("Nijie", "nijie", "followed"),
    "#class"   : nijie.NijieFollowedExtractor,
},

{
    "#url"     : "https://nijie.info/view.php?id=70720",
    "#category": ("Nijie", "nijie", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#sha1_url"     : "3d654e890212ba823c9647754767336aebc0a743",
    "#sha1_metadata": "41da5d0e178b04f01fe72460185df52fadc3c91b",
    "#sha1_content" : "d85e3ea896ed5e4da0bca2390ad310a4df716ca6",
},

{
    "#url"     : "https://nijie.info/view.php?id=70724",
    "#category": ("Nijie", "nijie", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://nijie.info/view_popup.php?id=70720",
    "#category": ("Nijie", "nijie", "image"),
    "#class"   : nijie.NijieImageExtractor,
},

)
