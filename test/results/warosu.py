# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import warosu


__tests__ = (
{
    "#url"     : "https://warosu.org/jp/thread/16656025",
    "#category": ("", "warosu", "thread"),
    "#class"   : warosu.WarosuThreadExtractor,
    "#urls"    : (
        "https://i.warosu.org/data/jp/img/0166/56/1488487280004.png",
        "https://i.warosu.org/data/jp/img/0166/56/1488493239417.png",
        "https://i.warosu.org/data/jp/img/0166/56/1488493636725.jpg",
        "https://i.warosu.org/data/jp/img/0166/56/1488493700040.jpg",
        "https://i.warosu.org/data/jp/img/0166/56/1488499585168.jpg",
        "https://i.warosu.org/data/jp/img/0166/56/1488530851199.jpg",
        "https://i.warosu.org/data/jp/img/0166/56/1488536072155.jpg",
        "https://i.warosu.org/data/jp/img/0166/56/1488603426484.png",
        "https://i.warosu.org/data/jp/img/0166/56/1488647021253.jpg",
        "https://i.warosu.org/data/jp/img/0166/56/1488866825031.jpg",
        "https://i.warosu.org/data/jp/img/0166/56/1489094956868.jpg",
    ),
},

{
    "#url"     : "https://warosu.org/jp/thread/16658073",
    "#category": ("", "warosu", "thread"),
    "#class"   : warosu.WarosuThreadExtractor,
    "#sha1_content" : "d48df0a701e6599312bfff8674f4aa5d4fb8db1c",
    "#urls"         : "https://i.warosu.org/data/jp/img/0166/58/1488521824388.jpg",
    "#count"        : 1,

    "board"     : "jp",
    "board_name": "Otaku Culture",
    "com"       : "Is this canon?",
    "ext"       : ".jpg",
    "extension" : "jpg",
    "filename"  : "sadako-vs-kayako-movie-review",
    "fsize"     : "55 KB",
    "h"         : 675,
    "image"     : "https://i.warosu.org/data/jp/img/0166/58/1488521824388.jpg",
    "name"      : "Anonymous",
    "no"        : 16658073,
    "now"       : "Fri, Mar 3, 2017 01:17:04",
    "thread"    : "16658073",
    "tim"       : 1488521824388,
    "time"      : 1488503824,
    "title"     : "Is this canon?",
    "w"         : 450,
},

{
    "#url"     : "https://warosu.org/jp/thread/45886210",
    "#comment" : "deleted post (#5289)",
    "#category": ("", "warosu", "thread"),
    "#class"   : warosu.WarosuThreadExtractor,
    "#count"   : "> 150",

    "board"     : "jp",
    "board_name": "Otaku Culture",
    "title"     : "/07/th Expansion Thread",
},

{
    "#url"     : "https://warosu.org/ic/thread/4604652",
    "#category": ("", "warosu", "thread"),
    "#class"   : warosu.WarosuThreadExtractor,
    "#pattern" : r"https://i.warosu\.org/data/ic/img/0046/04/1590\d{9}\.jpg",
    "#count"   : 133,

    "board"     : "ic",
    "board_name": "Artwork/Critique",
    "com"       : str,
    "ext"       : ".jpg",
    "filename"  : str,
    "fsize"     : str,
    "h"         : range(200, 3507),
    "image"     : r"re:https://i.warosu\.org/data/ic/img/0046/04/1590\d+\.jpg",
    "name"      : "re:Anonymous|Dhe Specky Spider-Man",
    "no"        : range(4604652, 4620000),
    "now"       : r"re:\w\w\w, \w\w\w \d\d?, 2020 \d\d:\d\d:\d\d",
    "thread"    : "4604652",
    "tim"       : range(1590430159651, 1590755510488),
    "time"      : range(1590415759, 1590755510),
    "title"     : "American Classic Comic Artists",
    "w"         : range(200, 3000),
},

)
