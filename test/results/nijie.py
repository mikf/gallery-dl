# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nijie
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://nijie.info/members.php?id=44",
    "#category": ("Nijie", "nijie", "user"),
    "#class"   : nijie.NijieUserExtractor,
    "#results" : (
        "https://nijie.info/members_illust.php?id=44",
        "https://nijie.info/members_dojin.php?id=44",
    ),
},

{
    "#url"     : "https://nijie.info/members_illust.php?id=44",
    "#category": ("Nijie", "nijie", "illustration"),
    "#class"   : nijie.NijieIllustrationExtractor,
    "#results": (
        "https://pic.nijie.net/__s4__/d7b5d8b576a90f3688cfe6bfa6ebb678817ecb4c19f118e187e0f039c81b2e5d0b6c2edfe359d9f65b457507bf9ae807801a0ac27b9cf06ee94e1cb848c75d2f31353acc3197dff04f537d70a7cb6b8782f6f0635de3f3d522e57827.jpg",
        "https://pic.nijie.net/__s4__/d7e2d9b124a95933ddc4e5baadbcb62b2a0ce7c6163dadac1d49c57e8da5d113398f3170da7835f03c897d9d6a9993d8fa40036a5209508611a305280cd684b33ca600f8160ee0d958b7c7f49972e4f4c650b8d58fff493a032d25f8.jpg",
    ),

    "artist_id"  : 44,
    "artist_name": "ED",
    "count"      : 1,
    "date"       : "type:datetime",
    "description": str,
    "extension"  : "jpg",
    "filename"   : str,
    "image_id"   : int,
    "num"        : 0,
    "tags"       : list,
    "title"      : str,
    "url"        : r"re:https://pic.nijie.net/__s4__/[0-9a-f]{184}.jpg$",
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
    "#results"      : "https://pic.nijie.net/__s4__/d7e2d9b124a95933ddc4e5baadbcb62b2a0ce7c6163dadac1d49c57e8da5d113398f3170da7835f03c897d9d6a9993d8fa40036a5209508611a305280cd684b33ca600f8160ee0d958b7c7f49972e4f4c650b8d58fff493a032d25f8.jpg",
    "#sha1_content" : "d85e3ea896ed5e4da0bca2390ad310a4df716ca6",

    "artist_id"  : 44,
    "artist_name": "ED",
    "count"      : 1,
    "date"       : "dt:2014-01-18 19:58:21",
    "description": "租絵にてお邪魔いたし候\r\n是非ともこの”おっぱい”をご高覧賜りたく馳せ参じた次第\r\n長文にて失礼仕る\r\n\r\nまず全景でありますが、首を右に傾けてみて頂きたい\r\nこの絵図は茶碗を眺めていた私が思わぬ美しさにて昇天したときのものを、筆をとり、したためたものである（トレースではない）\r\n筆は疾風の如く走り、半刻過ぎには私好みの”おっぱい”になっていたのである！\r\n次に細部をみて頂きたい\r\n絵図を正面から見直して頂くと、なんとはんなりと美しいお椀型をしたおっぱいであろうか　　右手から緩やかに生まれる曲線は左手に進むにつれて、穏やかな歪みを含み流れる　　これは所謂轆轤目であるが三重の紐でおっぱいをぐるぐると巻きつけた情景そのままであり、この歪みから茶碗の均整は崩れ、たぷんたぷんのおっぱいの重量感を醸し出している！\r\nさらに左手に進めば梅花皮（カイラギ）を孕んだ高大が現れる　今回は点線にて表現するが、その姿は乳首から母乳が噴出するが如く　或は精子をぶっかけられたが如く　白くとろっとした釉薬の凝固が素晴しい景色をつくりだしているのである！\r\n最後には極めつけ、すくっと螺旋を帯びながらそそり立つ兜巾（ときん）！この情景はまさしく乳首である！　　全体をふんわりと盛り上げさせる乳輪にちょこっと存在する乳頭はぺろりと舌で確かめ勃起させたくなる風情がある！\r\n\r\nこれを”おっぱい”と呼ばずなんと呼ぼうや！？\r\n\r\n興奮のあまり失礼致した\r\n御免",
    "extension"  : "jpg",
    "filename"   : "d7e2d9b124a95933ddc4e5baadbcb62b2a0ce7c6163dadac1d49c57e8da5d113398f3170da7835f03c897d9d6a9993d8fa40036a5209508611a305280cd684b33ca600f8160ee0d958b7c7f49972e4f4c650b8d58fff493a032d25f8",
    "image_id"   : 70720,
    "num"        : 0,
    "tags"       : ["おっぱい"],
    "title"      : "俺好高麗井戸茶碗　銘おっぱい",
    "url"        : "https://pic.nijie.net/__s4__/d7e2d9b124a95933ddc4e5baadbcb62b2a0ce7c6163dadac1d49c57e8da5d113398f3170da7835f03c897d9d6a9993d8fa40036a5209508611a305280cd684b33ca600f8160ee0d958b7c7f49972e4f4c650b8d58fff493a032d25f8.jpg",
    "user_id"    : 44,
    "user_name"  : "ED",
},

{
    "#url"     : "https://nijie.info/view.php?id=594044",
    "#comment" : "404",
    "#category": ("Nijie", "nijie", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://nijie.info/view.php?id=37078",
    "#comment" : "'view_side_dojin' thumbnails (#5049)",
    "#category": ("Nijie", "nijie", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#results" : "https://pic.nijie.net/__s4__/d7b5d9b470fa0d368bcbb0bda4bae2797380288fb3a6f2d9aa1899530bbc0453912f2397ee9a37dbbd992b5bbde36f86061910e06961837c0ae7629006732ef8581a512a0e0b454ca050fa793340367fbef201687f1b8cdb2692898b.jpg",
},

{
    "#url"     : "https://nijie.info/view.php?id=385585",
    "#comment" : "video (#5707)",
    "#category": ("Nijie", "nijie", "image"),
    "#class"   : nijie.NijieImageExtractor,
    "#results" : (
        "https://pic.nijie.net/__s4__/d7b884ee71f90f358fcfe0bbf2e7b57ac1b72bd5df705d984997b3d47968e387b4d2e33c04faa793c9bb26f3f005eb5f875b440fcabb36f02d811203325ce520aacc1581c0ea361906bd6877031942a2a340d44ff9ba3d9c23950d44.mp4",
        "https://pic.nijie.net/__s4__/d7e685e777ae0f308ecaeabda0e8e32c4a0873467846be7078716328f9b105bfc278d968db43d2707e577c63c231fb1a4999570823c460f18ee35b790f6e1c4a4c01a05a8c3260c2cd3b9f77810e5a1b2a22755f279f47cf86e75733.jpg",
        "https://pic.nijie.net/__s4__/d7b38cee78f80c678acae3bef2b9e32c0fd196fdafaed57c041390ac33dd8f23b3236a48d9d41c6081ce7ca79840caa7deacc0120a0dc516210e2925c954d79c08e94bb9c0f7c572bd174336f64e6924721a2727078df5ad48e77b1b.jpg",
    ),
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
