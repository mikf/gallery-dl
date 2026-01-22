# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo


__tests__ = (
{
    "#url"     : "https://celebforum.to/threads/addison-vodka.84947/post-885855",
    "#category": ("xenforo", "celebforum", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#results" : (
        "https://celebforum.to/data/assets/videos/notregistered.mp4",
        "https://celebforum.to/attachments/e2vurqbi2i-png.5293040/",
        "https://celebforum.to/attachments/wxt4sxsity-png.5293043/",
        "https://celebforum.to/attachments/echvvlmtcl-png.5293045/",
    ),

    "count"       : 4,
    "extension"   : {"png", "mp4"},
    "filename"    : str,
    "num_external": 0,
    "num_internal": range(1, 4),
    "type"        : {"video", "inline"},
    "post"        : {
        "attachments": "",
        "author"     : "kamikaze-770807",
        "author_id"  : "post-88585",
        "author_slug": "",
        "author_url" : "/threads/addison-vodka.84947/post-885855",
        "count"      : 4,
        "date"       : "dt:2024-09-15 08:08:16",
        "id"         : "885855",
        "content"    : str,
    },
    "thread"      : {
        "author"     : "Iomflj",
        "author_id"  : "",
        "author_slug": "iomflj",
        "author_url" : "",
        "date"       : "dt:2024-01-29 19:56:27",
        "id"         : "84947",
        "posts"      : int,
        "section"    : "Pornostars",
        "tags"       : (),
        "title"      : "Addison Vodka",
        "url"        : "https://celebforum.to/threads/addison-vodka.84947/",
        "views"      : -1,
    },
},

{
    "#url"     : "https://celebforum.to/threads/addison-vodka.84947/",
    "#category": ("xenforo", "celebforum", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
    "#count"   : range(1000, 2000),

    "count"       : int,
    "num"         : int,
    "num_external": int,
    "num_internal": int,
    "type"        : {"external", "inline", "video"},
    "post"        : {
        "attachments": str,
        "author"     : str,
        "author_id"  : str,
        "author_slug": str,
        "author_url" : str,
        "count"      : int,
        "date"       : "type:datetime",
        "id"         : str,
        "content"    : str
    },
    "thread"      : {
        "author"     : "Iomflj",
        "author_id"  : "",
        "author_slug": "iomflj",
        "author_url" : "",
        "date"       : "dt:2024-01-29 19:56:27",
        "id"         : "84947",
        "posts"      : int,
        "section"    : "Pornostars",
        "tags"       : (),
        "title"      : "Addison Vodka",
        "url"        : "https://celebforum.to/threads/addison-vodka.84947/",
        "views"      : -1,
    },
},

{
    "#url"     : "https://celebforum.to/forums/pornostars.13/",
    "#category": ("xenforo", "celebforum", "forum"),
    "#class"   : xenforo.XenforoForumExtractor,
    "#pattern" : xenforo.XenforoThreadExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://celebforum.to/media/albums/5404/",
    "#category": ("xenforo", "celebforum", "media-album"),
    "#class"   : xenforo.XenforoMediaAlbumExtractor,
},

)
