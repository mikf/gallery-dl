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
    "#class"   : patreon.PatreonCreatorExtractor,
    "#count"   : 1,

    "date": "dt:2020-03-30 21:21:44",
},

{
    "#url"     : "https://www.patreon.com/kovelianot",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.patreon.com/user?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user/posts/?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user?c=369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/id:369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/home",
    "#class"   : patreon.PatreonUserExtractor,
},

{
    "#url"     : "https://www.patreon.com/posts/precious-metal-23563293",
    "#comment" : "postfile + attachments",
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.patreon.com/posts/56127163",
    "#comment" : "account suspended",
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.patreon.com/posts/free-post-12497641",
    "#comment" : "tags (#1539)",
    "#class"   : patreon.PatreonPostExtractor,

    "tags": ["AWMedia"],
},

{
    "#url"     : "https://www.patreon.com/posts/m3u8-94714289",
    "#class"   : patreon.PatreonPostExtractor,
    "#pattern" : [
        r"https://c10\.patreonusercontent\.com/4/patreon-media/p/post/94714289/be3d8eb994ae44eca4baffcdc6dd25fc/eyJhIjoxLCJwIjoxfQ%3D%3D/1\.png",
        r"ytdl:https://www.patreon\.com/api/video/255859412/video\.m3u8",
    ]
},

{
    "#url"     : "https://www.patreon.com/posts/not-found-123",
    "#class"   : patreon.PatreonPostExtractor,
    "#exception": exception.NotFoundError,
},

)
