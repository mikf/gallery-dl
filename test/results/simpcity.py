# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import simpcity
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://simpcity.cr/threads/ririkana-rr_loveit.10731/post-1753131",
    "#class"   : simpcity.SimpcityPostExtractor,
    "#auth"    : True,
    "#results" : "https://jpg5.su/img/coWRwo",

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
<div class="bbWrapper"><a href="https://jpg5.su/img/coWRwo" target="_blank" class="link link--external" rel="noopener"><img src="https://simp6.jpg5.su/images/FqsNcNCaIAITBEL.md.jpg" data-url="https://simp6.jpg5.su/images/FqsNcNCaIAITBEL.md.jpg" class="bbImage " loading="lazy"
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
    "#class"   : simpcity.SimpcityPostExtractor,
    "#auth"     : False,
    "#exception": exception.AuthRequired,
},

{
    "#url"     : "https://simpcity.cr/threads/puutin_cos.219873/post-26053409",
    "#comment" : "iframe embeds (#8214)",
    "#class"   : simpcity.SimpcityPostExtractor,
    "#auth"    : True,
    "#results" : (
        "https://jpg5.su/img/NNFssUg",
        "https://saint2.cr/embed/nPy1kG3w55V",
        "https://saint2.cr/embed/c0KhPjU4-F3",
        "https://saint2.cr/embed/sZWnVZ_mQsV",
        "https://saint2.cr/embed/MEBiLx6DETQ",
    ),
},

{
    "#url"     : "https://simpcity.cr/threads/shinhashimoto00-shinhashimoto01.184378/post-13389764",
    "#comment" : "quote in post content (#8214)",
    "#class"   : simpcity.SimpcityPostExtractor,
    "#auth"    : True,
    "#results" : ("/goto/post?id=13358068", "https://cyberdrop.me/a/Sh9GlG38"),
},

{
    "#url"     : "https://simpcity.cr/threads/alua-tatakai.89490/",
    "#class"   : simpcity.SimpcityThreadExtractor,
    "#auth"    : True,
    "#pattern" : r"https://(jpg5\.su/img/\w+|bunkr\.\w+/[fiv]/\w+|pixeldrain.com/l/\w+|alua.com/tatakai)|/goto/post",
    "#count"   : 29,

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
    "#class"   : simpcity.SimpcityThreadExtractor,
},

{
    "#url"     : "https://simpcity.cr/forums/asians.48/",
    "#class"   : simpcity.SimpcityForumExtractor,
    "#pattern" : simpcity.SimpcityThreadExtractor.pattern,
    "#range"   : "1-100",
    "#count"   : 100,
},

)
