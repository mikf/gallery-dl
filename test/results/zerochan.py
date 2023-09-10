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
    "#pattern" : r"https://static\.zerochan\.net/.+\.full\.\d+\.(jpg|png)",
    "#count"   : "> 24",

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
        "Theme:Shirt",
        "Theme:Short Hair",
    ],
    "uploader": "YukinoTokisaki",
    "width"   : 1920,
},

)
