# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://simpcity.cr/threads/ririkana-rr_loveit.10731/post-1753131",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://jpg6.su/img/coWRwo",

    "count" : 1,
    "num"   : 1,
    "post"  : {
        "author"    : "Zebrabobinn",
        "author_id" : "171827",
        "author_url": "https://simpcity.cr/members/zebrabobinn.171827/",
        "count"     : 1,
        "date"      : "dt:2023-03-08 12:59:10",
        "id"        : "1753131",
        "content"   : """\
<div class="bbWrapper"><a href="https://jpg6.su/img/coWRwo" target="_blank" class="link link--external" rel="noopener"><img src="https://simp6.jpg6.su/images/FqsNcNCaIAITBEL.md.jpg" data-url="https://simp6.jpg6.su/images/FqsNcNCaIAITBEL.md.jpg" class="bbImage " loading="lazy"
\t\talt="FqsNcNCaIAITBEL.md.jpg" title="FqsNcNCaIAITBEL.md.jpg" style="" width="" height="" /></a></div>\
""",
    },
    "thread": {
        "author"    : "eula",
        "author_id" : "54987",
        "author_url": "https://simpcity.cr/members/eula.54987/",
        "date"      : "dt:2022-03-11 17:15:59",
        "id"        : "10731",
        "posts"     : range(320, 500),
        "section"   : "Asians",
        "title"     : "Ririkana | RR_loveit",
        "url"       : "https://simpcity.cr/threads/ririkana-rr_loveit.10731/",
        "views"     : range(790_000, 900_000),
        "tags"      : [
            "asian",
            "big ass",
            "gravure",
            "japanese",
            "japanese big ass",
            "small tits",
            "thicc",
        ],
    },
},

{
    "#url"     : "https://simpcity.cr/threads/ririkana-rr_loveit.10731/post-1753131",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"     : False,
    "#exception": exception.AuthRequired,
},

{
    "#url"     : "https://simpcity.cr/threads/puutin_cos.219873/post-26053409",
    "#comment" : "iframe embeds (#8214)",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : (
        "https://jpg6.su/img/NNFssUg",
        "https://saint2.cr/embed/nPy1kG3w55V",
        "https://saint2.cr/embed/c0KhPjU4-F3",
        "https://saint2.cr/embed/sZWnVZ_mQsV",
        "https://saint2.cr/embed/MEBiLx6DETQ",
    ),
},

{
    "#url"     : "https://simpcity.cr/threads/shinhashimoto00-shinhashimoto01.184378/post-13389764",
    "#comment" : "quote in post content (#8214)",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://cyberdrop.cr/a/Sh9GlG38",
},

{
    "#url"     : "https://simpcity.cr/threads/kayle-oralglory.36572/post-12065490",
    "#comment" : "deleted thread author (#8323)",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : (
        "https://redgifs.com/ifr/trainedovercookedsquid",
        "https://jpg6.su/img/aKroBJp",
        "https://jpg6.su/img/aKroy2E",
        "https://jpg6.su/img/aKrofqa",
        "https://jpg6.su/img/aKroDgo",
        "https://bunkr.cr/v/6sErIc9pjrnQ3",
    ),

    "post"  : {
        "author"    : "Hexorium",
        "author_id" : "3715883",
        "author_url": "https://simpcity.cr/members/hexorium.3715883/",
        "count"     : 6,
        "date"      : "dt:2024-12-15 21:37:05",
        "id"        : "12065490",
    },
    "thread": {
        "author"    : "Deleted member 166159",
        "author_id" : "166159",
        "author_url": "",
        "date"      : "dt:2022-04-05 14:48:14",
        "id"        : "36572",
        "section"   : "Premium Asians",
        "title"     : "Kayle OralGlory",
        "url"       : "https://simpcity.cr/threads/kayle-oralglory.36572/",
    },
},

{
    "#url"     : "https://simpcity.cr/threads/sophia-diamond.10049/post-10891",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : (
        "https://brandarmy.com/SophiaDiamond",
        "https://www.tiktok.com/@sophia.ilysm?lang=en",
        "https://www.instagram.com/sophiadiamond/",
        "https://simpcity.cr/attachments/sophiadiamond_239636842_558607608495946_5357173067872834144_n-jpg.65924/",
    ),

    "count"       : 4,
    "num"         : range(1, 4),
    "num_external": range(1, 3),
    "num_internal": {0, 1},
    "type"        : {"inline", "external"},
    "post"        : {
        "attachments": "",
        "author"     : "inoncognito",
        "author_id"  : "53824",
        "author_url" : "/members/inoncognito.53824/",
        "count"      : 4,
        "date"       : "dt:2022-03-11 00:41:28",
        "id"         : "10891",
        "content"    : str,
    },
    "thread"      : {
        "author"    : "inoncognito",
        "author_id" : "53824",
        "author_url": "https://simpcity.cr/members/inoncognito.53824/",
        "date"      : "dt:2022-03-11 00:41:28",
        "id"        : "10049",
        "posts"     : range(1_000, 2_000),
        "section"   : "TikTok",
        "title"     : "Sophia Diamond",
        "url"       : "https://simpcity.cr/threads/sophia-diamond.10049/",
        "views"     : range(4_200_000, 6_000_000),
        "tags"      : [
            "busty",
            "diamond",
            "slut",
            "sophia",
            "sophiadiamond",
            "tease",
            "teen",
            "tiktok",
            "tits",
        ],
    },
},

{
    "#url"     : "https://simpcity.cr/threads/sophia-diamond.10049/post-18744",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://simpcity.cr/attachments/sophiadiamondcancunbikiniwp-png.36179/",

    "count"       : 1,
    "extension"   : "png",
    "filename"    : "SophiaDiamondCancunBikiniWP",
    "id"          : 36179,
    "num"         : 1,
    "num_external": 0,
    "num_internal": 1,
    "type"        : "inline",
    "post"        : {
        "author"     : "ElyseGooner",
        "author_id"  : "65059",
        "author_url" : "https://simpcity.cr/members/elysegooner.65059/",
        "count"      : 1,
        "date"       : "dt:2022-03-11 22:39:06",
        "id"         : "18744",
        "attachments": str,
        "content"    : r're:<div class="bbWrapper">Collage</div>\s+</div>',
    },
    "thread"      : {
        "date"      : "dt:2022-03-11 00:41:28",
        "id"        : "10049",
        "section"   : "TikTok",
        "title"     : "Sophia Diamond",
    },
},

{
    "#url"     : "https://simpcity.cr/threads/lustn4lexi-hot4lexi-lexi-2-legit-hott4lexi-lexi.175167/post-2512729",
    "#comment" : "'Click here to load redgifs media' (#8609)",
    "#category": ("xenforo", "simpcity", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://redgifs.com/ifr/unusedsubmissivemullet",
},

{
    "#url"     : "https://simpcity.cr/threads/alua-tatakai.89490/",
    "#category": ("xenforo", "simpcity", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
    "#auth"    : True,
    "#pattern" : r"https://(jpg6\.su/img/\w+|bunkr\.\w+/[fiv]/\w+|pixeldrain.com/l/\w+|alua.com/tatakai)|saint2.cr/embed",
    "#count"   : range(100, 300),

    "count" : int,
    "num"   : int,
    "post"  : {
        "author"    : str,
        "author_id" : r"re:\d+",
        "author_url": str,
        "content"   : str,
        "count"     : int,
        "date"      : "type:datetime",
        "id"        : r"re:\d+",
    },
    "thread": {
        "author"    : "Ekalamosus",
        "author_id" : "1036155",
        "author_url": "https://simpcity.cr/members/ekalamosus.1036155/",
        "date"      : "dt:2022-07-31 15:40:14",
        "id"        : "89490",
        "posts"     : 45,
        "section"   : "Asians",
        "title"     : "Alua tatakai",
        "url"       : "https://simpcity.cr/threads/alua-tatakai.89490/",
        "views"     : range(47_000, 60_000),
        "tags"      : [
            "alter",
            "alua",
            "pinay",
        ],
    },
},

{
    "#url"     : "https://simpcity.su/threads/angel-chan-wlep-wlop-menruinyanko_.12948/",
    "#category": ("xenforo", "simpcity", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
},

{
    "#url"     : "https://simpcity.cr/forums/asians.48/",
    "#category": ("xenforo", "simpcity", "forum"),
    "#class"   : xenforo.XenforoForumExtractor,
    "#pattern" : xenforo.XenforoThreadExtractor.pattern,
    "#range"   : "1-100",
    "#count"   : 100,
},

)
