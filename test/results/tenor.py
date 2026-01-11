# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tenor


__tests__ = (
{
    "#url"  : "https://tenor.com/view/moving-gif-8525772382434057283",
    "#class": tenor.TenorImageExtractor,
    "#results": "https://media1.tenor.com/m/dlGgz3LRXEMAAAAC/moving.gif",

    "bg_color" : "",
    "description": "an illustration of a tree with green leaves",
    "created"  : 1687512768.687436,
    "date"     : "dt:2023-06-23 09:32:48",
    "embed"    : r"re:<div class=.+",
    "extension": "gif",
    "filename" : "moving",
    "!h1_title": "Moving Sticker",
    "hasaudio" : False,
    "format"   : "gif",
    "width"    : 467,
    "height"   : 498,
    "size"     : 60157,
    "duration" : 0,
    "id"       : "8525772382434057283",
    "id_format": "dlGgz3LRXEMAAAAC",
    "index"    : 0,
    "itemurl"  : "https://tenor.com/view/moving-gif-8525772382434057283",
    "long_title": "Moving Sticker - Moving Stickers",
    "media_formats": dict,
    "policy_status": "POLICY_STATUS_UNSPECIFIED",
    "shares"   : range(70_000, 200_000),
    "source_id": "",
    "title"    : "Moving Sticker",
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
    "#results": "https://media.tenor.com/dlGgz3LRXEMAAAAx/moving.webp",

    "format"   : "webp",
    "width"    : 468,
    "height"   : 498,
    "size"     : 9808,
    "duration" : 0,
    "id"       : "8525772382434057283",
    "id_format": "dlGgz3LRXEMAAAAx",
},

{
    "#url"    : "https://tenor.com/view/vtuber-hololive-%E3%83%9B%E3%83%AD%E3%83%A9%E3%82%A4%E3%83%96-hologra-%E3%83%9B%E3%83%AD%E3%81%90%E3%82%89-gif-26058046",
    "#comment": "non-ASCII characters in URL",
    "#class"  : tenor.TenorImageExtractor,
    "#results": "https://media1.tenor.com/m/jHugoUKy-T0AAAAC/vtuber-hololive.gif",

    "id": "10122861201914526013",
},

{
    "#url"  : "https://tenor.com/ja/view/moving-gif-8525772382434057283",
    "#class": tenor.TenorImageExtractor,
},

{
    "#url"     : "https://tenor.com/view/dance-dancing-rhythm-music-party-gif-10174070686436479501",
    "#class"   : tenor.TenorImageExtractor,
    "#results" : "https://media1.tenor.com/m/jTGPYoDC0g0AAAAC/dance-dancing.gif",

    "bg_color"     : "",
    "created"      : 1761968378.53755,
    "date"         : "dt:2025-11-01 03:39:38",
    "description"  : "a blue and white penguin with the word pengu written below it",
    "duration"     : 1.4,
    "embed"        : """<div class="tenor-gif-embed" data-postid="10174070686436479501" data-share-method="host" data-aspect-ratio="1" data-width="100%"><a href="https://tenor.com/view/dance-dancing-rhythm-music-party-gif-10174070686436479501">Dance Dancing Sticker</a>from <a href="https://tenor.com/search/dance-stickers">Dance Stickers</a></div> <script type="text/javascript" async src="https://tenor.com/embed.js"></script>""",
    "extension"    : "gif",
    "filename"     : "dance-dancing",
    "flags"        : ["sticker"],
    "format"       : "gif",
    "hasaudio"     : False,
    "height"       : 498,
    "id"           : "10174070686436479501",
    "id_format"    : "jTGPYoDC0g0AAAAC",
    "index"        : 0,
    "itemurl"      : "https://tenor.com/view/dance-dancing-rhythm-music-party-gif-10174070686436479501",
    "legacy_info"  : {"post_id": "0"},
    "long_title"   : "Dance Dancing Sticker - Dance Dancing Rhythm Stickers",
    "policy_status": "POLICY_STATUS_UNSPECIFIED",
    "shares"       : range(20_000, 200_000),
    "size"         : 379845,
    "source_id"    : "",
    "title"        : "Dance Dancing Sticker",
    "url"          : "https://tenor.com/mhJvX13UBsL.gif",
    "width"        : 498,
    "media_formats": dict,
    "tags"         : [
        "dance",
        "dancing",
        "rhythm",
        "music",
        "party",
        "happy",
        "meme",
        "funny",
        "dancer",
        "cute",
        "excited",
        "pengu",
        "pudgy",
        "penguin",
        "pudgypenguins",
    ],
    "user"         : {
        "flags"        : ["partner"],
        "partnername"  : "Pudgy Penguins",
        "profile_id"   : "7220590138123212970",
        "tagline"      : "Pudgy Penguins supplying the internet with good vibes",
        "url"          : "https://tenor.com/official/PudgyPenguins",
        "userid"       : "12680456",
        "username"     : "PudgyPenguins",
        "usertype"     : "partner",
    },
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
    "#results": "https://media1.tenor.com/m/1auSjzCikuoAAAAC/2016-roblox.gif",

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
