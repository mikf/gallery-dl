# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tenor


__tests__ = (
{
    "#url"  : "https://tenor.com/view/moving-gif-8525772382434057283",
    "#class": tenor.TenorImageExtractor,
    "#urls" : "https://media1.tenor.com/m/dlGgz3LRXEMAAAAC/moving.gif",

    "bg_color" : "",
    "content_description": "an illustration of a tree with green leaves",
    "created"  : 1687512768.687436,
    "date"     : "dt:2023-06-23 09:32:48",
    "embed"    : r"re:<div class=.+",
    "extension": "gif",
    "filename" : "moving",
    "h1_title" : "Moving Sticker",
    "hasaudio" : False,
    "width"    : 467,
    "height"   : 498,
    "id"       : "8525772382434057283",
    "index"    : 0,
    "itemurl"  : "https://tenor.com/view/moving-gif-8525772382434057283",
    "long_title": "Moving Sticker - Moving Stickers",
    "media_formats": dict,
    "policy_status": "POLICY_STATUS_UNSPECIFIED",
    "shares"   : range(40000, 60000),
    "source_id": "",
    "title"    : "Moving Sti",
    "url"      : "https://tenor.com/kjYh53rdMGt.gif",
    "flags"    : [
        "static",
        "sticker",
    ],
    "legacy_info": {
        "post_id": "200777050"
    },
    "tags": [
        "moving",
    ],
    "user": {
        "avatars"     : {},
        "flags"       : [],
        "partnerbanner": {},
        "partnercategories": [],
        "partnerlinks": [],
        "partnername" : "",
        "profile_id"  : "11989898659889539214",
        "tagline"     : "",
        "url"         : "https://tenor.com/users/imenabdelmalek",
        "userid"      : "0",
        "username"    : "imenabdelmalek",
        "usertype"    : "user",
    },
},

{
    "#url"    : "https://tenor.com/view/moving-gif-8525772382434057283",
    "#comment": "'format' option",
    "#class"  : tenor.TenorImageExtractor,
    "#options": {"format": ["mkv", "foobar", "webp"]},
    "#urls"   : "https://media.tenor.com/dlGgz3LRXEMAAAAx/moving.webp",
},

{
    "#url"  : "https://tenor.com/ja/view/moving-gif-8525772382434057283",
    "#class": tenor.TenorImageExtractor,
},

{
    "#url"    : "https://tenor.com/search/trees-gifs",
    "#class"  : tenor.TenorSearchExtractor,
    "#pattern": r"https://media\d+\.tenor\.com/m/[\w-]+/[\w%-]+\.gif",
    "#range"  : "1-80",
    "#count"  : 80,

    "search_tags": "trees",
},

{
    "#url"  : "https://tenor.com/en-GB/search/trees-gifs",
    "#class": tenor.TenorSearchExtractor,
},

{
    "#url"    : "https://tenor.com/search/trees-water-wind-sun-%3C&%3E-gifs",
    "#class"  : tenor.TenorSearchExtractor,
    "#pattern": r"https://media\d+\.tenor\.com/m/[\w-]+/[\w%-]+\.gif",
    "#range"  : "1-80",
    "#count"  : 80,

    "search_tags": "trees water wind sun <&>",
},

{
    "#url"    : "https://tenor.com/users/robloxfan123",
    "#class"  : tenor.TenorUserExtractor,
    "#urls"   : "https://media1.tenor.com/m/1auSjzCikuoAAAAC/2016-roblox.gif",

    "user": {
        "profile_id": "8180139772821505417",
        "url"       : "https://tenor.com/users/ROBLOXfan123",
        "userid"    : "11206759",
        "username"  : "ROBLOXfan123",
        "usertype"  : "user",
    },
},

{
    "#url"    : "https://tenor.com/users/annetv",
    "#class"  : tenor.TenorUserExtractor,
    "#pattern": r"https://media\d+\.tenor\.com/m/[\w-]+/[\w%-]+\.gif",
    "#count"  : range(70, 100),

    "user": {
        "profile_id": "14727075564983373376",
        "url"       : "https://tenor.com/users/annetv",
        "userid"    : "8529134",
        "username"  : "annetv",
    },
},

{
    "#url"  : "https://tenor.com/official/rwrbonprime",
    "#class": tenor.TenorUserExtractor,
    "#range": "1",

    "user": {
        "avatars"      : dict,
        "flags"        : ["partner"],
        "partnerbanner": dict,
        "partnercategories": [],
        "partnercta"   : {
            "text": "Learn More",
            "url" : "https://www.amazon.com/dp/B0BYSWHGB9",
        },
        "partnerlinks" : list,
        "partnername"  : "Red, White & Royal Blue",
        "profile_id"   : "9116468280322048077",
        "tagline"      : "Love is about to get royally complicated",
        "url"          : "https://tenor.com/official/RWRBonPrime",
        "userid"       : "0",
        "username"     : "RWRBonPrime",
        "usertype"     : "partner",
    },
},

)
