# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo


__tests__ = (
{
    "#url"     : "https://titsintops.com/phpBB2/threads/mia-big-titty-boston-blonde.13575039/post-3265146",
    "#category": ("xenforo", "titsintops", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#results" : (
        "https://titsintops.com/phpBB2/attachments/img_3763-webp.6091490/",
        "https://titsintops.com/phpBB2/attachments/img_3765-webp.6091491/",
        "https://titsintops.com/phpBB2/attachments/img_3755-webp.6091492/",
        "https://titsintops.com/phpBB2/attachments/img_3754-webp.6091493/",
        "https://titsintops.com/phpBB2/attachments/img_3753-webp.6091494/",
        "https://titsintops.com/phpBB2/attachments/img_3759-webp.6091495/",
        "https://titsintops.com/phpBB2/attachments/img_3751-webp.6091496/",
    ),

    "count"       : 7,
    "num"         : range(1, 7),
    "num_internal": range(1, 7),
    "num_external": 0,
    "extension"   : "webp",
    "filename"    : str,
    "id"          : range(6091490, 6091496),
    "type"        : "inline",
    "post"        : {
        "author"     : "Nsfwev",
        "author_id"  : "1178301",
        "author_slug": "nsfwev",
        "author_url" : "https://titsintops.com/phpBB2/members/nsfwev.1178301/",
        "count"      : 7,
        "date"       : "dt:2025-08-27 05:39:53",
        "id"         : "3265146",
        "attachments": str,
        "content"    : """re:<b>soo hot one of my favorites</b>""",
    },
    "thread"      : {
        "author"     : "lazywriterx",
        "author_id"  : "323115",
        "author_slug": "lazywriterx",
        "author_url" : "https://titsintops.com/phpBB2/members/lazywriterx.323115/",
        "date"       : "dt:2025-05-02 13:33:58",
        "id"         : "13575039",
        "posts"      : range(3, 10),
        "section"    : "Tits in Tops & Social Media",
        "title"      : "Mia - Big titty Boston blonde",
        "url"        : "https://titsintops.com/phpBB2/threads/mia-big-titty-boston-blonde.13575039/",
        "views"      : range(2_000, 10_000),
        "tags"       : [
            "big tit blonde",
            "blonde",
        ],
    },
},

{
    "#url"     : "https://titsintops.com/phpBB2/threads/mia-big-titty-boston-blonde.13575039/",
    "#category": ("xenforo", "titsintops", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
    "#pattern" : r"https://titsintops\.com/phpBB2/attachments/.+",
    "#count"   : range(13, 100),

    "extension"   : "webp",
    "id"          : int,
    "type"        : "inline",
    "post"        : dict,
    "thread"      : {
        "author"     : "lazywriterx",
        "author_id"  : "323115",
        "author_slug": "lazywriterx",
        "author_url" : "https://titsintops.com/phpBB2/members/lazywriterx.323115/",
        "date"       : "dt:2025-05-02 13:33:58",
        "id"         : "13575039",
        "section"    : "Tits in Tops & Social Media",
        "title"      : "Mia - Big titty Boston blonde",
        "url"        : "https://titsintops.com/phpBB2/threads/mia-big-titty-boston-blonde.13575039/",
        "tags"       : [
            "big tit blonde",
            "blonde",
        ],
    },
},

{
    "#url"     : "https://titsintops.com/phpBB2/forums/tits-in-tops-social-media.1/",
    "#category": ("xenforo", "titsintops", "forum"),
    "#class"   : xenforo.XenforoForumExtractor,
    "#pattern" : xenforo.XenforoThreadExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

)
