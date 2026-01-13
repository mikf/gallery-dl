# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo


__tests__ = (
{
    "#url"     : "https://nudostar.com/forum/threads/tate-mcrae.109528/post-1919100",
    "#category": ("xenforo", "nudostarforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : (
        "https://imagetwist.com/bvolb8129fnm/v1.jpg",
        "https://imagetwist.com/9pddder15iow/v2.jpg",
        "https://imagetwist.com/zzonmk0gqqdv/v3.jpg",
    ),

    "count"       : 3,
    "type"        : "external",
    "post"        : {
        "attachments": "",
        "author"     : "djokica",
        "author_id"  : "3471965",
        "author_url" : "/forum/members/djokica.3471965/",
        "author_slug": "djokica",
        "content"    : """<div class="bbWrapper"><a href="https://imagetwist.com/bvolb8129fnm/v1.jpg" target="_blank" class="link link--external" rel="nofollow noopener"><img src="https://s10.imagetwist.com/th/73048/bvolb8129fnm.jpg" data-url="https://s10.imagetwist.com/th/73048/bvolb8129fnm.jpg" class="bbImage " style="" alt="" title="" /></a> <a href="https://imagetwist.com/9pddder15iow/v2.jpg" target="_blank" class="link link--external" rel="nofollow noopener"><img src="https://s10.imagetwist.com/th/73048/9pddder15iow.jpg" data-url="https://s10.imagetwist.com/th/73048/9pddder15iow.jpg" class="bbImage " style="" alt="" title="" /></a> <a href="https://imagetwist.com/zzonmk0gqqdv/v3.jpg" target="_blank" class="link link--external" rel="nofollow noopener"><img src="https://s10.imagetwist.com/th/73048/zzonmk0gqqdv.jpg" data-url="https://s10.imagetwist.com/th/73048/zzonmk0gqqdv.jpg" class="bbImage " style="" alt="" title="" /></a></div>""",
        "count"      : 3,
        "date"       : "dt:2025-10-31 21:26:42",
        "id"         : "1919100",
    },
    "thread"      : {
        "author"    : "djokica",
        "author_id" : "",
        "author_url": "",
        "date"      : "dt:2024-06-05 00:00:00",
        "id"        : "109528",
        "posts"     : range(20, 80),
        "section"   : "Celebrity",
        "tags"      : (),
        "title"     : "Tate Mcrae",
        "url"       : "https://nudostar.com/forum/threads/tate-mcrae.109528/",
        "views"     : -1,
    },
},

{
    "#url"     : "https://nudostar.com/forum/threads/name.12345/post-67890",
    "#category": ("xenforo", "nudostarforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
},

{
    "#url"     : "https://nudostar.com/forum/threads/aspen-rae.106714/",
    "#category": ("xenforo", "nudostarforum", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
},

{
    "#url"     : "https://nudostar.com/forum/threads/aspen-rae.106714/page-2",
    "#category": ("xenforo", "nudostarforum", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
},

{
    "#url"     : "https://nudostar.com/forum/forums/celebrity.14/",
    "#category": ("xenforo", "nudostarforum", "forum"),
    "#class"   : xenforo.XenforoForumExtractor,
    "#pattern" : xenforo.XenforoThreadExtractor.pattern,
    "#range"   : "1-100",
    "#count"   : 100,
},

)
