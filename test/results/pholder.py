# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pholder


__tests__ = (
{
    "#url"     : "https://pholder.com/r/lavaporn",
    "#class"   : pholder.PholderSubredditExtractor,
    "#range"   : "1-20",
    "#count"   : 20,

    "ad_allowlist"  : None,
    "author"        : str,
    "comment"       : str,
    "date"          : "type:datetime",
    "extension"     : {"jpg", "gif"},
    "filename"      : str,
    "gallery_id"    : "",
    "width"         : {int, None},
    "height"        : {int, None},
    "id"            : str,
    "is_gallery"    : False,
    "network"       : "reddit",
    "not_found"     : False,
    "nsfw"          : 0,
    "origin"        : str,
    "profile"       : r"re:https://www.reddit.com/u/.+",
    "submitted_utc" : int,
    "subredditTitle": "lavaporn",
    "tags"          : {list, tuple, None},
    "thumbnails"    : list,
    "title"         : str,
},

{
    "#url"     : "https://pholder.com/u/automoderator",
    "#class"   : pholder.PholderUserExtractor,
    "#range"   : "1-20",
    "#count"   : ">= 20",

    "author": "AutoModerator",
},

{
    "#url"     : "https://pholder.com/search-text",
    "#category": ("", "pholder", "search"),
    "#class"   : pholder.PholderSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

)
