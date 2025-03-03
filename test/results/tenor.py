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
    "embed"    : "<div class=\"tenor-gif-embed\" data-postid=\"8525772382434057283\" data-share-method=\"host\" data-aspect-ratio=\"0.937751\" data-width=\"100%\"><a href=\"https://tenor.com/view/moving-gif-8525772382434057283\">Moving Sticker</a>from <a href=\"https://tenor.com/search/moving-stickers\">Moving Stickers</a></div> <script type=\"text/javascript\" async src=\"https://tenor.com/embed.js\"></script>",
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
    "shares"   : 42528,
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
    "#url"    : "https://tenor.com/search/trees-gifs",
    "#class"  : tenor.TenorSearchExtractor,
    "#pattern": r"https://media\d+\.tenor\.com/m/[\w-]+/[\w%-]+\.gif",
    "#range"  : "1-80",
    "#count"  : 80,

    "search_tags": "trees",
},

{
    "#url"    : "https://tenor.com/search/trees-water-wind-sun-%3C&%3E-gifs",
    "#class"  : tenor.TenorSearchExtractor,
    "#pattern": r"https://media\d+\.tenor\.com/m/[\w-]+/[\w%-]+\.gif",
    "#range"  : "1-80",
    "#count"  : 80,

    "search_tags": "trees water wind sun <&>",
},

)
