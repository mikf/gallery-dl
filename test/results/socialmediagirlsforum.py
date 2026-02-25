# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo


__tests__ = (
{
    "#url"     : "https://forums.socialmediagirls.com/threads/clara-jenyfer-clarajenyferr.482246/post-4743566",
    "#category": ("xenforo", "socialmediagirlsforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://pixeldrain.com/u/zHNNuNqF",

    "count"       : 1,
    "num"         : 1,
    "num_external": 1,
    "num_internal": 0,
    "type"        : "external",
    "post"        : {
        "attachments": "",
        "author"     : "gat0deb0tas",
        "author_id"  : "4665384",
        "author_slug": "gat0deb0tas",
        "author_url" : "https://forums.socialmediagirls.com/members/gat0deb0tas.4665384/",
        "count"      : 1,
        "date"       : "dt:2025-09-03 22:15:05",
        "id"         : "4743566",
        "content"    : str,
    },
    "thread"      : {
        "author"     : "Arrascaeta_14",
        "author_id"  : "4736433",
        "author_slug": "arrascaeta_14",
        "author_url" : "https://forums.socialmediagirls.com/members/arrascaeta_14.4736433/",
        "date"       : "dt:2025-09-02 17:33:45",
        "id"         : "482246",
        "posts"      : range(11, 50),
        "section"    : "Instagram Models",
        "tags"       : (),
        "title"      : "Clara jenyfer - clarajenyferr",
        "url"        : "https://forums.socialmediagirls.com/threads/clara-jenyfer-clarajenyferr.482246/",
        "views"      : range(14_000, 80_000),
    },
},

{
    "#url"     : "https://forums.socialmediagirls.com/threads/nilce-moretto.64148/post-2803132",
    "#comment" : "imgur s9e media embed iframe (#9127)",
    "#category": ("xenforo", "socialmediagirlsforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#auth"    : True,
    "#results" : "https://imgur.com/a/TluZbDn",
},

{
    "#url"     : "https://forums.socialmediagirls.com/threads/casallr.435949/unread",
    "#category": ("xenforo", "socialmediagirlsforum", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
    "#auth"    : True,
    "#pattern" : r"https://(pixeldrain\.com/|gofile\.io|\w+\.erome\.com)",
    "#count"   : 13,

    "count"       : int,
    "type"        : "external",
    "post"        : dict,
    "thread"      : {
        "author"     : "Deleted member 379830",
        "author_id"  : "379830",
        "author_slug": "deleted-member-379830",
        "author_url" : "https://forums.socialmediagirls.com/members/deleted-member-379830.379830/",
        "date"       : "dt:2025-01-24 17:49:20",
        "id"         : "435949",
        "posts"      : 3,
        "section"    : "Instagram Models",
        "title"      : "Casallr",
        "url"        : "https://forums.socialmediagirls.com/threads/casallr.435949/",
        "views"      : range(10_000, 50_000),
        "tags"       : [
            "amador",
            "casal",
            "safada",
            "swing",
        ],
    },
},

{
    "#url"     : "https://forums.socialmediagirls.com/forums/bikini-girls.80/",
    "#category": ("xenforo", "socialmediagirlsforum", "forum"),
    "#class"   : xenforo.XenforoForumExtractor,
    "#pattern" : xenforo.XenforoThreadExtractor.pattern,
    "#auth"    : True,
    "#range"   : "1-50",
    "#count"   : 50,
},

)
