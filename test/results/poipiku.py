# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import poipiku


__tests__ = (
{
    "#url"     : "https://poipiku.com/25049/",
    "#class"   : poipiku.PoipikuUserExtractor,
    "#pattern" : r"https://cdn.poipiku.com/\d+/\d+_\w+\.(jpe?g|png)\?.+",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://poipiku.com/IllustListPcV.jsp?PG=1&ID=25049&KWD=",
    "#class"   : poipiku.PoipikuUserExtractor,
},

{
    "#url"     : "https://poipiku.com/25049/5864576.html",
    "#class"   : poipiku.PoipikuPostExtractor,
    "#pattern" : r"https://cdn.poipiku.com/000025049/005864576_EWN1Y65gQ\.png\?Expires=\d+&Signature=.+&Key-Pair-Id=\w+$",

    "count"        : 1,
    "description"  : "",
    "original"     : True,
    "extension"    : "png",
    "filename"     : "005864576_EWN1Y65gQ",
    "num"          : 1,
    "post_category": "DOODLE",
    "post_id"      : "5864576",
    "user_id"      : "25049",
    "user_name"    : "ユキウサギ",
},

{
    "#url"     : "https://poipiku.com/25049/5864576.html",
    "#class"   : poipiku.PoipikuPostExtractor,
    "#auth"    : False,
    "#results" : "https://cdn.poipiku.com/000025049/005864576_EWN1Y65gQ.png_640.jpg",

    "count"        : 1,
    "description"  : "",
    "original"     : False,
    "extension"    : "jpg",
    "filename"     : "005864576_EWN1Y65gQ.png_640",
    "num"          : 1,
    "post_category": "DOODLE",
    "post_id"      : "5864576",
    "user_id"      : "25049",
    "user_name"    : "ユキウサギ",
},

{
    "#url"     : "https://poipiku.com/2166245/6411749.html",
    "#class"   : poipiku.PoipikuPostExtractor,
    "#pattern" : r"https://cdn.poipiku.com/002166245/006411749(_\d+)?_\w+.jpeg\?Expires=\d+&Signature=.+",
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
    "#class"   : poipiku.PoipikuPostExtractor,
    "#pattern" : r"https://cdn.poipiku.com/003572553/005776587(_\d+)?_\w+.jpeg\?Expires=\d+&Signature=.+",
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
    "#class"   : poipiku.PoipikuPostExtractor,
    "#pattern" : r"https://cdn.poipiku.com/001400760/005483268_JdB7sAWpv.jpeg\?Expires=\d+&Signature=.+",

    "count"        : 1,
    "num"          : 1,
    "description"  : "えち描く描く詐欺ずっとやってるのですこしかいてた<br />ほたしか写ってないよ",
    "warning"      : True,
    "post_category": "TRAINING",
    "post_id"      : "5483268",
    "user_id"      : "1400760",
    "user_name"    : "onitsuraaaai",
},

{
    "#url"     : "https://poipiku.com/12282220/12290661.html",
    "#comment" : "Password Required ('yes')",
    "#class"   : poipiku.PoipikuPostExtractor,
    "#options" : {"password": "yes"},
    "#pattern" : (
        r"https://cdn.poipiku.com/012282220/012290661_cTNUS0cX9.png\?.+",
        r"https://cdn.poipiku.com/012282220/012290661_027772303_q9Yb5mdQO.png\?.+",
        r"https://cdn.poipiku.com/012282220/012290661_027772304_jTlthEwKf.jpeg\?.+",
    ),

    "count"        : 3,
    "num"          : range(1, 3),
    "filename"     : str,
    "extension"    : {"jpeg", "png"},
    "description"  : "过去的🕶️Σ🕶️ 🔞<br />堆堆<br /><br />18↑ yes/no",
    "original"     : True,
    "password"     : True,
    "post_category": "DOODLE",
    "post_id"      : "12290661",
    "user_id"      : "12282220",
    "user_name"    : "FaratMo4",
},

{
    "#url"     : "https://poipiku.com/3572553/5776587.html",
    "#comment" : "SPOILER / Warning (warning.png)",
    "#class"   : poipiku.PoipikuPostExtractor,
},

{
    "#url"     : "https://poipiku.com/9117461/12291186.html",
    "#comment" : "Follower Only (publish_follower.png)  + Password ('yes')",
    "#class"   : poipiku.PoipikuPostExtractor,
},

{
    "#url"     : "https://poipiku.com/11516189/12291094.html",
    "#comment" : "Retweet Required (publish_t_rt.png) + Password",
    "#class"   : poipiku.PoipikuPostExtractor,
},

{
    "#url"     : "https://poipiku.com/542956/12293287.html",
    "#comment" : "Sign-In Only (publish_login.png)",
    "#class"   : poipiku.PoipikuPostExtractor,
    "#auth"    : False,
},

{
    "#url"     : "https://poipiku.com/11513074/12290032.html",
    "#comment" : "Sign-In Only (publish_login.png) + Password",
    "#class"   : poipiku.PoipikuPostExtractor,
    "#metadata": "post",
    "#auth"    : False,

    "requires": "login",
    "password": True,
},

{

    "#url"     : "https://poipiku.com/2498939/12293054.html",
    "#comment" : "Animated GIF",
    "#class"   : poipiku.PoipikuPostExtractor,
    "#auth"    : False,
    "#result"  : "https://cdn.poipiku.com/002498939/012293054_RcNvVjZ85.gif_640.jpg",
    "#sha1_content": "ac4726b93dc6d507188cfcb5193dd20bcf6c38b0",
},

{

    "#url"     : "https://poipiku.com/11329926/11669296.html",
    "#comment" : "Text Posts",
    "#class"   : poipiku.PoipikuPostExtractor,
},

)
