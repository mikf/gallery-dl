# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tapas


__tests__ = (
{
    "#url"     : "https://tapas.io/series/just-leave-me-be",
    "#category": ("", "tapas", "series"),
    "#class"   : tapas.TapasSeriesExtractor,
    "#pattern" : r"https://us-a\.tapas\.io/pc/\w\w/[0-9a-f-]+\.jpg",
    "#count"   : 132,
},

{
    "#url"     : "https://tapas.io/series/yona",
    "#comment" : "mature",
    "#category": ("", "tapas", "series"),
    "#class"   : tapas.TapasSeriesExtractor,
    "#count"   : 26,
},

{
    "#url"     : "https://tapas.io/episode/2068651",
    "#category": ("", "tapas", "episode"),
    "#class"   : tapas.TapasEpisodeExtractor,
    "#pattern" : "^text:",
    "#sha1_url": "0b53644c864a0a097f65accea6bb620be9671078",

    "book"            : True,
    "comment_cnt"     : int,
    "date"            : "dt:2021-02-23 16:02:07",
    "early_access"    : False,
    "escape_title"    : "You are a Tomb Raider (2)",
    "free"            : True,
    "id"              : 2068651,
    "like_cnt"        : int,
    "liked"           : bool,
    "mature"          : False,
    "next_ep_id"      : 2068652,
    "nsfw"            : False,
    "nu"              : False,
    "num"             : 1,
    "open_comments"   : True,
    "pending_scene"   : 2,
    "prev_ep_id"      : 2068650,
    "publish_date"    : "2021-02-23T16:02:07Z",
    "read"            : bool,
    "related_ep_id"   : None,
    "relative_publish_date": "Feb 23, 2021",
    "scene"           : 2,
    "scheduled"       : False,
    "title"           : "You are a Tomb Raider (2)",
    "unlock_cnt"      : 0,
    "unlocked"        : False,
    "view_cnt"        : int,
    "series"          : {
        "genre"         : dict,
        "has_book_cover": True,
        "has_top_banner": True,
        "id"            : 199931,
        "premium"       : True,
        "sale_type"     : "WAIT_OR_MUST_PAY",
        "subscribed"    : bool,
        "thumbsup_cnt"  : int,
        "title"         : "Tomb Raider King",
        "type"          : "BOOKS",
        "url"           : "tomb-raider-king-novel",
    },
},

{
    "#url"     : "https://tapas.io/SANG123/series",
    "#comment" : "#5306",
    "#category": ("", "tapas", "creator"),
    "#class"   : tapas.TapasCreatorExtractor,
    "#urls"    : (
        "https://tapas.io/series/the-return-of-the-disaster-class-hero-novel",
        "https://tapas.io/series/the-return-of-the-disaster-class-hero",
        "https://tapas.io/series/tomb-raider-king",
        "https://tapas.io/series/tomb-raider-king-novel",
    ),
},

)
