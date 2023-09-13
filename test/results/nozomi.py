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
    "#pattern"     : r"https://w\.nozomi\.la/2/15/aaa9f7c632cde1e1a5baaff3fb6a6d857ec73df7fdc5cf5a358caf604bf73152\.webp",
    "#sha1_url"    : "e5525e717aec712843be8b88592d6406ae9e60ba",
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
    "#count"        : 7,
    "#sha1_url"     : "fb956ccedcf2cf509739d26e2609e910244aa56c",
    "#sha1_metadata": "516ca5cbd0d2a46a8ce26679d6e08de5ac42184b",
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
    "#pattern"     : r"https://g\.nozomi\.la/a/f0/d1b06469e00d72e4f6346209c149db459d76b58a074416c260ed93cc31fa9f0a\.gif",
    "#sha1_content": "952efb78252bbc9fb56df2e8fafb68d5e6364181",
},

{
    "#url"     : "https://nozomi.la/post/2269847.html",
    "#comment" : "video",
    "#category": ("", "nozomi", "post"),
    "#class"   : nozomi.NozomiPostExtractor,
    "#pattern"     : r"https://v\.nozomi\.la/d/0e/ff88398862669783691b31519f2bea3a35c24b6e62e3ba2d89b4409e41c660ed\.webm",
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
    "#pattern" : r"^https://[wgv]\.nozomi\.la/\w/\w\w/\w+\.\w+$",
    "#range"   : "1-25",
    "#count"   : ">= 25",
},

{
    "#url"     : "https://nozomi.la/search.html?q=hibiscus%203:4_ratio#1",
    "#category": ("", "nozomi", "search"),
    "#class"   : nozomi.NozomiSearchExtractor,
    "#count"   : ">= 5",
},

)
