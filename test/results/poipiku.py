# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import poipiku


__tests__ = (
{
    "#url"     : "https://poipiku.com/25049/",
    "#category": ("", "poipiku", "user"),
    "#class"   : poipiku.PoipikuUserExtractor,
    "#pattern" : r"https://img-org\.poipiku\.com/user_img\d+/000025049/\d+_\w+\.(jpe?g|png)$",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://poipiku.com/IllustListPcV.jsp?PG=1&ID=25049&KWD=",
    "#category": ("", "poipiku", "user"),
    "#class"   : poipiku.PoipikuUserExtractor,
},

{
    "#url"     : "https://poipiku.com/25049/5864576.html",
    "#category": ("", "poipiku", "post"),
    "#class"   : poipiku.PoipikuPostExtractor,
    "#pattern" : r"https://img-org\.poipiku\.com/user_img\d+/000025049/005864576_EWN1Y65gQ\.png$",

    "count"        : 1,
    "description"  : "",
    "extension"    : "png",
    "filename"     : "005864576_EWN1Y65gQ",
    "num"          : 1,
    "post_category": "DOODLE",
    "post_id"      : "5864576",
    "user_id"      : "25049",
    "user_name"    : "ユキウサギ",
},

{
    "#url"     : "https://poipiku.com/2166245/6411749.html",
    "#category": ("", "poipiku", "post"),
    "#class"   : poipiku.PoipikuPostExtractor,
    "#pattern" : r"https://img-org\.poipiku\.com/user_img\d+/002166245/006411749_\w+\.jpeg$",
    "#count"   : 4,

    "count"        : 4,
    "num"          : range(1, 4),
    "description"  : "絵茶の産物ネタバレあるやつ",
    "post_category": "SPOILER",
    "post_id"      : "6411749",
    "user_id"      : "2166245",
    "user_name"    : "wadahito",
},

{
    "#url"     : "https://poipiku.com/3572553/5776587.html",
    "#comment" : "different warning button style",
    "#category": ("", "poipiku", "post"),
    "#class"   : poipiku.PoipikuPostExtractor,
    "#pattern" : r"https://img-org\.poipiku.com/user_img\d+/003572553/005776587_(\d+_)?\w+\.jpeg$",
    "#count"   : 3,

    "count"        : 3,
    "num"          : range(1, 3),
    "description"  : "ORANGE OASISボスネタバレ<br />曲も大好き<br />2枚目以降はほとんど見えなかった1枚目背景のヒエログリフ小ネタです𓀀",
    "post_category": "SPOILER",
    "post_id"      : "5776587",
    "user_id"      : "3572553",
    "user_name"    : "nagakun",
},

{
    "#url"     : "https://poipiku.com/1400760/5483268.html",
    "#comment" : "Warning and no 'Show all' button (#6736)",
    "#category": ("", "poipiku", "post"),
    "#class"   : poipiku.PoipikuPostExtractor,
    "#urls"    : "https://img-org.poipiku.com/user_img02/001400760/005483268_JdB7sAWpv.jpeg",

    "count"        : 1,
    "num"          : 1,
    "description"  : "えち描く描く詐欺ずっとやってるのですこしかいてた<br />ほたしか写ってないよ",
    "post_category": "TRAINING",
    "post_id"      : "5483268",
    "user_id"      : "1400760",
    "user_name"    : "onitsuraaaai",
},

)
