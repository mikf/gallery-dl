# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import patreon
import datetime
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.patreon.com/koveliana",
    "#category": ("", "patreon", "creator"),
    "#class"   : patreon.PatreonCreatorExtractor,
    "#range"   : "1-15",
    "#count"   : 15,

    "attachments"  : list,
    "comment_count": int,
    "content"      : str,
    "creator"      : dict,
    "date"         : datetime.datetime,
    "id"           : int,
    "images"       : list,
    "like_count"   : int,
    "post_type"    : str,
    "published_at" : str,
    "title"        : str,
},

{
    "#url"     : "https://www.patreon.com/koveliana/posts?filters[month]=2020-3",
    "#category": ("", "patreon", "creator"),
    "#class"   : patreon.PatreonCreatorExtractor,
    "#count"   : 1,

    "date": "dt:2020-03-30 21:21:44",
},

{
    "#url"     : "https://www.patreon.com/kovelianot",
    "#category": ("", "patreon", "creator"),
    "#class"   : patreon.PatreonCreatorExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.patreon.com/user?u=2931440",
    "#category": ("", "patreon", "creator"),
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user/posts/?u=2931440",
    "#category": ("", "patreon", "creator"),
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user?c=369707",
    "#category": ("", "patreon", "creator"),
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/id:369707",
    "#category": ("", "patreon", "creator"),
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/home",
    "#category": ("", "patreon", "user"),
    "#class"   : patreon.PatreonUserExtractor,
},

{
    "#url"     : "https://www.patreon.com/posts/precious-metal-23563293",
    "#comment" : "postfile + attachments",
    "#category": ("", "patreon", "post"),
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.patreon.com/posts/56127163",
    "#comment" : "postfile + content",
    "#category": ("", "patreon", "post"),
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 3,

    "filename": r"re:^(?!1).+$",
},

{
    "#url"     : "https://www.patreon.com/posts/free-post-12497641",
    "#comment" : "tags (#1539)",
    "#category": ("", "patreon", "post"),
    "#class"   : patreon.PatreonPostExtractor,

    "tags": ["AWMedia"],
},

{
    "#url"     : "https://www.patreon.com/posts/meu8-94714289",
    "#category": ("", "patreon", "post"),
    "#class"   : patreon.PatreonPostExtractor,
    "#range"   : "2",
    "#pattern" : r"ytdl:https://stream\.mux\.com/NLrxTLdxyGStpOgapJAtB8uPGAaokEcj8YovML00y2DY\.m3u8\?token=ey.+",
},

{
    "#url"     : "https://www.patreon.com/posts/not-found-123",
    "#category": ("", "patreon", "post"),
    "#class"   : patreon.PatreonPostExtractor,
    "#exception": exception.NotFoundError,
},

)
