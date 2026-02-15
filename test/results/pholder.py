# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pholder


__tests__ = (
{
    "#url"     : "https://pholder.com/r/lavaporn",
    "#category": ("", "pholder", "subreddit"),
    "#class"   : pholder.PholderSubredditExtractor,
    "#range"   : "1-20",
    "#count"   : ">= 20",
},

{
    "#url"     : "https://pholder.com/r/lavaporn/",
    "#category": ("", "pholder", "subreddit"),
    "#class"   : pholder.PholderSubredditExtractor,
},

{
    "#url"     : "https://pholder.com/u/automoderator",
    "#category": ("", "pholder", "user"),
    "#class"   : pholder.PholderUserExtractor,
    "#range"   : "1-20",
    "#count"   : ">= 20",
},

{
    "#url"     : "https://pholder.com/u/automoderator/",
    "#category": ("", "pholder", "user"),
    "#class"   : pholder.PholderUserExtractor,
},

{
    "#url"     : "https://pholder.com/search-text",
    "#category": ("", "pholder", "search"),
    "#class"   : pholder.PholderSearchExtractor,
    "#range"   : "1-10",
    "#count"   : "== 10",
},

)
