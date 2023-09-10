# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import subscribestar
import datetime


__tests__ = (
{
    "#url"     : "https://www.subscribestar.com/subscribestar",
    "#category": ("", "subscribestar", "user"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#pattern" : r"https://(ss-uploads-prod\.b-cdn|\w+\.cloudfront)\.net/uploads(_v2)?/users/11/",
    "#count"   : ">= 20",

    "author_id"  : 11,
    "author_name": "subscribestar",
    "author_nick": "SubscribeStar",
    "content"    : str,
    "date"       : datetime.datetime,
    "id"         : int,
    "num"        : int,
    "post_id"    : int,
    "type"       : r"re:image|video|attachment",
    "url"        : str,
    "?pinned"    : bool,
},

{
    "#url"     : "https://www.subscribestar.com/subscribestar",
    "#category": ("", "subscribestar", "user"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#options" : {"metadata": True},
    "#range"   : "1",

    "date": datetime.datetime,
},

{
    "#url"     : "https://subscribestar.adult/kanashiipanda",
    "#category": ("", "subscribestar", "user-adult"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.subscribestar.com/posts/102468",
    "#category": ("", "subscribestar", "post"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#count"   : 1,

    "author_id"  : 11,
    "author_name": "subscribestar",
    "author_nick": "SubscribeStar",
    "content"    : r"re:<h1>Brand Guidelines and Assets</h1>",
    "date"       : "dt:2020-05-07 12:33:00",
    "extension"  : "jpg",
    "filename"   : "8ff61299-b249-47dc-880a-cdacc9081c62",
    "group"      : "imgs_and_videos",
    "height"     : 291,
    "id"         : 203885,
    "num"        : 1,
    "pinned"     : False,
    "post_id"    : 102468,
    "type"       : "image",
    "width"      : 700,
},

{
    "#url"     : "https://subscribestar.adult/posts/22950",
    "#category": ("", "subscribestar", "post-adult"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#count"   : 1,

    "date": "dt:2019-04-28 07:32:00",
},

)
