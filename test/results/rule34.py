# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v02


__tests__ = (
{
    "#url"     : "https://rule34.xxx/index.php?page=post&s=list&tags=danraku",
    "#category": ("gelbooru_v02", "rule34", "tag"),
    "#class"   : gelbooru_v02.GelbooruV02TagExtractor,
    "#results"     : (
        "https://wimg.rule34.xxx/images/4615/00722987a1e8b5617a15a20c19a0915157048d3b.jpg",
        "https://wimg.rule34.xxx/images/1845/04981deeac105a9c5fedc34a6ff017789e74f2a8.jpg",
    ),
    "#sha1_content": [
        "5c6ae9ee13e6d4bc9cb8bdce224c84e67fbfa36c",
        "622e80be3f496672c44aab5c47fbc6941c61bc79",
        "1e0dced55bcb5eefe5cc32f69c7a8df35547b459",
    ],

    "search_tags" : "danraku",
    "search_count": 2,
},

{
    "#url"     : "https://rule34.xxx/index.php?page=pool&s=show&id=179",
    "#category": ("gelbooru_v02", "rule34", "pool"),
    "#class"   : gelbooru_v02.GelbooruV02PoolExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://rule34.xxx/index.php?page=favorites&s=view&id=1030218",
    "#category": ("gelbooru_v02", "rule34", "favorite"),
    "#class"   : gelbooru_v02.GelbooruV02FavoriteExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://www.rule34.xxx/index.php?page=post&s=view&id=863",
    "#comment" : "www subdomain",
    "#category": ("gelbooru_v02", "rule34", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
},

{
    "#url"     : "https://rule34.xxx/index.php?page=post&s=view&id=863",
    "#category": ("gelbooru_v02", "rule34", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#options"     : {
        "tags" : True,
        "notes": True,
    },
    "#results"     : r"https://wimg.rule34.xxx/images/1/6aafbdb3e22f3f3b412ea2cf53321317a37063f3.jpg",
    "#sha1_content": [
        "a43f418aa350039af0d11cae501396a33bbe2201",
        "67b516295950867e1c1ab6bc13b35d3b762ed2a3",
    ],

    "tags_artist"   : "reverse_noise yamu_(reverse_noise)",
    "tags_character": "hong_meiling",
    "tags_copyright": "team_shanghai_alice touhou",
    "tags_general"  : str,
    "tags_metadata" : "censored translated",
    "notes"         : [
        {
            "body"  : "It feels angry, I'm losing myself... It won't calm down!",
            "height": 65,
            "id"    : 93586,
            "width" : 116,
            "x"     : 22,
            "y"     : 333,
        },
        {
            "body"  : "REPUTATION OF RAGE",
            "height": 272,
            "id"    : 93587,
            "width" : 199,
            "x"     : 78,
            "y"     : 442,
        },
    ],
},

{
    "#url"     : "https://rule34.xxx/index.php?page=post&s=view&id=13853212",
    "#comment" : "HTML response with 'api-cdn.' subdomain (#7697)",
    "#category": ("gelbooru_v02", "rule34", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#results" : "https://wimg.rule34.xxx/images/2164/60d61d06f3cd51be5152852d9c642d80.jpeg",
    "#sha1_content": [
        "0a07eb9e871589a012ec922c71eb4640fce09bb2",
    ],
},

)
