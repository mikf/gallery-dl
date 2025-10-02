# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nozomi


__tests__ = (
{
    "#url"     : "https://nozomi.la/post/3649262.html",
    "#category": ("", "nozomi", "post"),
    "#class"   : nozomi.NozomiPostExtractor,
    "#results"     : "https://w.gold-usergeneratedcontent.net/2/15/aaa9f7c632cde1e1a5baaff3fb6a6d857ec73df7fdc5cf5a358caf604bf73152.webp",
    "#sha1_content": "6d62c4a7fea50c0a89d499603c4e7a2b4b9bffa8",

    "artist"   : ["hammer (sunset beach)"],
    "character": ["patchouli knowledge"],
    "copyright": ["touhou"],
    "dataid"   : r"re:aaa9f7c632cde1e1a5baaff3fb6a6d857ec73df7fdc5",
    "date"     : "dt:2016-07-26 02:32:03",
    "extension": "webp",
    "filename" : str,
    "height"   : 768,
    "is_video" : False,
    "postid"   : 3649262,
    "tags"     : list,
    "type"     : "jpg",
    "url"      : str,
    "width"    : 1024,
},

{
    "#url"     : "https://nozomi.la/post/25588032.html",
    "#comment" : "multiple images per post",
    "#category": ("", "nozomi", "post"),
    "#class"   : nozomi.NozomiPostExtractor,
    "#results" : (
        "https://w.gold-usergeneratedcontent.net/3/94/085e55e355808c03dedbe74fe44db1c07435e071952e8b925a3dfe5ec3278943.webp",
        "https://w.gold-usergeneratedcontent.net/e/78/0fb5675f47e981650ab7a549cc8d90230ab0d249f35247258f6a7ceb81dd578e.webp",
        "https://w.gold-usergeneratedcontent.net/3/68/f3cde060f8e9047171bebb70e62947375ef6bdc0160f2f37ea4d5d25ebfde683.webp",
        "https://w.gold-usergeneratedcontent.net/e/41/888f1c268928adf77de609b50ade88a40f117b737cbaa1bdc264ccc2d074641e.webp",
        "https://w.gold-usergeneratedcontent.net/6/c0/d035d2851a6e8b24473d1c575e3f3df1cbee5ad2b002758c3546439dc959bc06.webp",
        "https://w.gold-usergeneratedcontent.net/b/b4/c527b2c6dde4124bdb8d7c0f061a03743aee36ccd2c8f707fd347674fc4e2b4b.webp",
        "https://w.gold-usergeneratedcontent.net/9/3a/c8b6f23fc86669724373c89d436fbc33b47078a38457243d24e80e76ad7e43a9.webp",
    ),
},

{
    "#url"     : "https://nozomi.la/post/130309.html",
    "#comment" : "empty 'date' (#1163)",
    "#category": ("", "nozomi", "post"),
    "#class"   : nozomi.NozomiPostExtractor,

    "date": None,
},

{
    "#url"     : "https://nozomi.la/post/1647.html",
    "#comment" : "gif",
    "#category": ("", "nozomi", "post"),
    "#class"   : nozomi.NozomiPostExtractor,
    "#results"     : "https://g.gold-usergeneratedcontent.net/a/f0/d1b06469e00d72e4f6346209c149db459d76b58a074416c260ed93cc31fa9f0a.gif",
    "#sha1_content": "952efb78252bbc9fb56df2e8fafb68d5e6364181",
},

{
    "#url"     : "https://nozomi.la/post/2269847.html",
    "#comment" : "video",
    "#category": ("", "nozomi", "post"),
    "#class"   : nozomi.NozomiPostExtractor,
    "#results"     : "https://v.gold-usergeneratedcontent.net/d/0e/ff88398862669783691b31519f2bea3a35c24b6e62e3ba2d89b4409e41c660ed.webm",
    "#sha1_content": "57065e6c16da7b1c7098a63b36fb0c6c6f1b9bca",
},

{
    "#url"     : "https://nozomi.la/",
    "#category": ("", "nozomi", "index"),
    "#class"   : nozomi.NozomiIndexExtractor,
},

{
    "#url"     : "https://nozomi.la/index-2.html",
    "#category": ("", "nozomi", "index"),
    "#class"   : nozomi.NozomiIndexExtractor,
},

{
    "#url"     : "https://nozomi.la/index-Popular-33.html",
    "#category": ("", "nozomi", "index"),
    "#class"   : nozomi.NozomiIndexExtractor,
},

{
    "#url"     : "https://nozomi.la/tag/3:1_aspect_ratio-1.html",
    "#category": ("", "nozomi", "tag"),
    "#class"   : nozomi.NozomiTagExtractor,
    "#pattern" : r"^https://[wgv]\.gold-usergeneratedcontent\.net/\w/\w\w/\w+\.\w+$",
    "#range"   : "1-25",
    "#count"   : ">= 25",
},

{
    "#url"     : "https://nozomi.la/search.html?q=hibiscus%203:4_ratio#1",
    "#category": ("", "nozomi", "search"),
    "#class"   : nozomi.NozomiSearchExtractor,
    "#count"   : range(5, 10),
},

{
    "#url"     : "https://nozomi.la/search.html?q=musume_janakute_mama_ga_sukinano!?",
    "#comment" : "404 error due to unquoted '?' in search tag (#8328)",
    "#class"   : nozomi.NozomiSearchExtractor,
    "#range"   : "1-3",
    "#count"   : 3,

    "search_tags": ["musume_janakute_mama_ga_sukinano!?"],
},

)
