# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nekohouse


__tests__ = (
{
    "#url"     : "https://nekohouse.su/fantia/user/319092/post/3163233",
    "#class"   : nekohouse.NekohousePostExtractor,
    "#urls"    : (
        "https://nekohouse.su/data/b2/ca/b2ca86189cda7408d75c36d850ca6394c089786d46c6dd0c90b4a2e17e07774f.jpg",
        "https://nekohouse.su/data/2e/cf/2ecfd1a04affa35c147bb43d626d6149c2c3f9a9fb7df1659a40c8de1b3e09e5.jpg",
        "https://nekohouse.su/data/9a/ed/9aed4b879023b761882c7c11ce74a3ee51a22487e2c77df0bfabed7c5a73cbe5.jpg",
    ),

    "content"  : "エリー・マナ・マリア編のもの\n\n会場行った人以外よくわからないと思うので、\nレポの体をなしてないですが…",
    "count"    : 3,
    "date"     : "dt:2024-12-12 09:34:36",
    "extension": "jpg",
    "filename" : r"re:^[0-9a-f]{64}$",
    "hash"     : r"re:^[0-9a-f]{64}$",
    "id"       : {"662005", "662006", "662007"},
    "num"      : range(1, 3),
    "post_id"  : "3163233",
    "service"  : "fantia",
    "title"    : "ルミナスバースデーイベ２",
    "type"     : "file",
    "url"      : str,
    "user_id"  : "319092",
    "username" : "島田フミカネ",
},

{
    "#url"     : "https://nekohouse.su/fantia/user/19235/post/2621173",
    "#comment" : "attachment / video",
    "#class"   : nekohouse.NekohousePostExtractor,
    "#range"   : "6",
    "#urls"    : (
        "https://nekohouse.su/data/f9/4c/f94ca55a329604bec63536828a36fd2b455aec03ffb3657e25c0b405d8484823.mp4",
    ),

    "content"  : "",
    "count"    : 6,
    "date"     : "dt:2024-03-15 12:09:48",
    "extension": "mp4",
    "filename" : "レミリアゲームver0.01",
    "hash"     : "f94ca55a329604bec63536828a36fd2b455aec03ffb3657e25c0b405d8484823",
    "id"       : "",
    "num"      : 6,
    "post_id"  : "2621173",
    "service"  : "fantia",
    "title"    : "ふたなりレミリア総受けエロゲーのお話",
    "type"     : "attachment",
    "url"      : "https://nekohouse.su/data/f9/4c/f94ca55a329604bec63536828a36fd2b455aec03ffb3657e25c0b405d8484823.mp4",
    "user_id"  : "19235",
    "username" : "なまこ大爆発",
},

{
    "#url"     : "https://nekohouse.su/fantia/user/19235",
    "#class"   : nekohouse.NekohouseUserExtractor,
    "#pattern" : r"https://nekohouse\.su/fantia/user/19235/post/\d+",
    "#count"   : range(51, 100),
},

)
