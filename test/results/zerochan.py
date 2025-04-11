# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import zerochan


__tests__ = (
{
    "#url"     : "https://www.zerochan.net/Perth+%28Kantai+Collection%29",
    "#category": ("booru", "zerochan", "tag"),
    "#class"   : zerochan.ZerochanTagExtractor,
    "#pattern" : r"https://static\.zerochan\.net/\.full\.\d+\.jpg",
    "#count"   : "> 50",

    "extension"  : r"jpg",
    "file_url"   : r"re:https://static\.zerochan\.net/\.full\.\d+\.jpg",
    "filename"   : r"re:\.full\.\d+",
    "height"     : int,
    "id"         : int,
    "search_tags": "Perth (Kantai Collection)",
    "tag"        : r"re:(Perth \(Kantai Collection\)|Kantai Collection)",
    "tags"       : list,
    "width"      : int,
},

{
    "#url"     : "https://www.zerochan.net/Perth+%28Kantai+Collection%29",
    "#category": ("booru", "zerochan", "tag"),
    "#class"   : zerochan.ZerochanTagExtractor,
    "#options" : {"pagination": "html"},
    "#pattern" : r"https://static\.zerochan\.net/.+\.full\.\d+\.(jpg|png)",
    "#count"   : "> 45",

    "extension"  : r"re:jpg|png",
    "file_url"   : r"re:https://static\.zerochan\.net/.+\.full\.\d+\.(jpg|png)",
    "filename"   : r"re:(Perth\.\(Kantai\.Collection\)|Kantai\.Collection)\.full\.\d+",
    "height"     : r"re:^\d+$",
    "id"         : r"re:^\d+$",
    "name"       : r"re:(Perth \(Kantai Collection\)|Kantai Collection)",
    "search_tags": "Perth (Kantai Collection)",
    "size"       : r"re:^\d+k$",
    "width"      : r"re:^\d+$",
},

{
    "#url"     : "https://www.zerochan.net/2920445",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#pattern" : r"https://static\.zerochan\.net/Perth\.%28Kantai\.Collection%29\.full.2920445\.jpg",
    "#auth"    : True,

    "author"  : "YeFan 葉凡",
    "date"    : "dt:2020-04-24 21:33:44",
    "file_url": "https://static.zerochan.net/Perth.%28Kantai.Collection%29.full.2920445.jpg",
    "filename": "Perth.(Kantai.Collection).full.2920445",
    "height"  : 1366,
    "id"      : 2920445,
    "path"    : [
        "Kantai Collection",
        "Perth (Kantai Collection)",
    ],
    "size"    : 1975296,
    "source"  : "",
    "tags"    : [
        "Mangaka:YeFan 葉凡",
        "Game:Kantai Collection",
        "Character:Perth (Kantai Collection)",
        "Theme:Blonde Hair",
        "Theme:Braids",
        "Theme:Coat",
        "Theme:Female",
        "Theme:Firefighter Outfit",
        "Theme:Group",
        "Theme:Long Sleeves",
        "Theme:Personification",
        "Theme:Pins",
        "Theme:Ribbon",
        "Theme:Short Hair",
        "Theme:Top",
    ],
    "uploader": "YukinoTokisaki",
    "width"   : 1920,
},

{
    "#url"     : "https://www.zerochan.net/2920445",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#pattern" : r"https://static\.zerochan\.net/Perth\.%28Kantai\.Collection%29\.full.2920445\.jpg",
    "#auth"    : False,

    "author"  : "YeFan 葉凡",
    "date"    : "dt:2020-04-24 21:33:44",
    "file_url": "https://static.zerochan.net/Perth.%28Kantai.Collection%29.full.2920445.jpg",
    "filename": "Perth.(Kantai.Collection).full.2920445",
    "height"  : 1366,
    "id"      : 2920445,
    "path"    : [
        "Kantai Collection",
        "Perth (Kantai Collection)",
    ],
    "size"    : 1975296,
    "source"  : "",
    "tags"    : [
        "Mangaka:YeFan 葉凡",
        "Game:Kantai Collection",
        "Character:Perth (Kantai Collection)",
        "Theme:Firefighter Outfit",
        "Theme:Pins",
    ],
    "uploader": "YukinoTokisaki",
    "width"   : 1920,
},

{
    "#url"     : "https://www.zerochan.net/4233756",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#urls"    : "https://static.zerochan.net/DRAGON.BALL.full.4233756.jpg",
    "#options" : {"tags": True},

    "author"   : "Raydash",
    "date"     : "dt:2024-07-23 00:10:51",
    "extension": "jpg",
    "file_url" : "https://static.zerochan.net/DRAGON.BALL.full.4233756.jpg",
    "filename" : "DRAGON.BALL.full.4233756",
    "height"   : 1125,
    "id"       : 4233756,
    "path"     : [
        "Manga",
        "DRAGON BALL",
    ],
    "size"     : 136192,
    "source"   : "https://x.com/Raydash30/status/1766012730769862774",
    "tags"     : [
        "Mangaka:Raydash",
        "Series:DRAGON BALL",
        "Series:DRAGON BALL Z",
        "Character:Piccolo",
        "Character:Son Gohan",
        "Theme:Duo",
        "Theme:Green Skin",
        "Theme:Male",
        "Theme:Male Focus",
        "Theme:Two Males",
        "Source:Fanart",
        "Source:Fanart from X (Twitter)",
        "Source:X (Twitter)",
    ],
    "tags_character": [
        "Piccolo",
        "Son Gohan",
    ],
    "tags_mangaka"  : [
        "Raydash",
    ],
    "tags_series"   : [
        "DRAGON BALL",
        "DRAGON BALL Z",
    ],
    "tags_source"   : [
        "Fanart",
        "Fanart from X (Twitter)",
        "X (Twitter)",
    ],
    "tags_theme"    : [
        "Duo",
        "Green Skin",
        "Male",
        "Male Focus",
        "Two Males",
    ],
    "uploader" : "menotbug",
    "width"    : 750,
},

{
    "#url"     : "https://www.zerochan.net/4233756",
    "#class"   : zerochan.ZerochanImageExtractor,
    "#auth"    : False,
    "#urls"    : "https://static.zerochan.net/DRAGON.BALL.full.4233756.jpg",

    "source"   : "https://x.com/Raydash30/status/1766012730769862774",
    "tags"     : [
        "Mangaka:Raydash",
        "Series:DRAGON BALL",
        "Series:DRAGON BALL Z",
        "Character:Piccolo",
        "Character:Son Gohan",
        "Theme:Green Skin",
        "Source:Fanart",
        "Source:Fanart from X (Twitter)",
        "Source:X (Twitter)",
    ],
},

{
    "#url"     : "https://www.zerochan.net/1395035",
    "#comment" : "Invalid control character '\r' in 'source' field (#5892)",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#auth"    : True,
    "#options" : {"metadata": True},

    "source": "http://www.youtube.com/watch?v=0vodqkGPxt8",
},

{
    "#url"     : "https://www.zerochan.net/4354955",
    "#comment" : "unescaped quotes in 'JSON' data (#6632)",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#auth"    : False,
    "#options" : {"metadata": True},

    "author"  : "SEGA",
    "date"    : "dt:2024-12-05 06:06:14",
    "file_url": "https://static.zerochan.net/Miles.%22Tails%22.Prower.full.4354955.jpg",
    "filename": "Miles.\"Tails\".Prower.full.4354955",
    "height"  : 705,
    "id"      : 4354955,
    "name"    : "Miles \"Tails\" Prower",
    "size"    : 252928,
    "source"  : "https://x.com/kellanstover/status/1580237736874606597",
    "uploader": "Anima-Chao",
    "width"   : 4096,
    "path"    : [
        "Sonic the Hedgehog",
        "Miles \"Tails\" Prower",
    ],
    "tags"    : [
        "Male",
        "Animal",
        "Fox",
        "Sonic the Hedgehog",
        "Flying",
        "Character Sheet",
        "Airplane",
        "SEGA",
        "Miles \"Tails\" Prower",
        "Official Art",
        "Midair",
        "X (Twitter)",
        "Sonic Origins",
        "Official Art from X",
        "Tory Patterson",
    ],
},

{
    "#url"     : "https://www.zerochan.net/4354955",
    "#comment" : "quotes in HTML tags",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#auth"    : False,
    "#options" : {"metadata": False},

    "tags": [
        "Mangaka:Tory Patterson",
        "Studio:SEGA",
        "Game:Sonic Origins",
        "Series:Sonic the Hedgehog",
        "Character:Miles \"Tails\" Prower",
        "Theme:Airplane",
        "Theme:Flying",
        "Theme:Fox",
        "Source:Character Sheet",
        "Source:Official Art",
        "Source:Official Art from X",
        "Source:X (Twitter)",
    ],
},

{
    "#url"     : "https://www.zerochan.net/2275437",
    "#comment" : "unicode escapes with surrogate pair (#7178)",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#auth"    : False,
    "#options" : {"metadata": False},

    "author"   : "MAYO🍚",
    "date"     : "dt:2018-02-25 16:03:48",
    "extension": "png",
    "file_url" : "https://static.zerochan.net/Kongou.full.2275437.png",
    "filename" : "Kongou.full.2275437",
    "width"    : 1047,
    "height"   : 1365,
    "id"       : 2275437,
    "size"     : 502784,
    "source"   : "",
    "uploader" : "SubaruSumeragi",
    "path"     : [
        "Kantai Collection",
        "Kongou",
    ],
    "tags"     : [
        "Mangaka:MAYO🍚",
        "Game:Kantai Collection",
        "Character:Kongou"
    ],
},

{
    "#url"     : "https://www.zerochan.net/4147104",
    "#comment" : "no 'author' in JSON-LD data (#7282)",
    "#category": ("booru", "zerochan", "image"),
    "#class"   : zerochan.ZerochanImageExtractor,
    "#auth"    : False,

    "author"   : "",
    "date"     : "dt:2024-04-02 12:09:30",
    "extension": "jpg",
    "file_url" : "https://static.zerochan.net/Lycoris.Recoil.full.4147104.jpg",
    "filename" : "Lycoris.Recoil.full.4147104",
    "width"    : 1061,
    "height"   : 1500,
    "id"       : 4147104,
    "size"     : 224256,
    "source"   : "https://twitter.com/animetv_jp/status/1775101399648374835/",
    "uploader" : "cutesherry",
    "path"     : [
        "Lycoris Recoil",
    ],
    "tags"     : [
        "Studio:A-1 Pictures",
        "Series:Lycoris Recoil",
        "Character:Inoue Takina",
        "Character:Nishikigi Chisato",
        "Theme:Bench",
        "Theme:Cherry Tree",
        "Theme:Floating Hair",
        "Theme:Sitting On Bench",
        "Theme:Sneakers",
        "Theme:Spring",
        "Source:Key Visual",
        "Source:Official Art",
    ],
},

)
