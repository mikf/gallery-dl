# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import sexcom


__tests__ = (
{
    "#url"     : "https://www.sex.com/pin/21241874-sexy-ecchi-girls-166/",
    "#comment" : "picture (legacy URL)",
    "#category": ("", "sexcom", "pin"),
    "#class"   : sexcom.SexcomPinExtractor,
    "#skip"    : "legacy",
    "#results"     : "https://imagex1.sx.cdn.live/images/pinporn/2014/08/26/7637609.jpg",
    "#sha1_content": "8cd419c6790ef7348bd398c364ab10f956e438dc",

    "comments" : range(0, 5),
    "date"     : "dt:2014-10-19 15:45:44",
    "date_url" : "dt:2014-08-26 00:00:00",
    "extension": "jpg",
    "filename" : "7637609",
    "likes"    : range(240, 275),
    "pin_id"   : 21241874,
    "repins"   : range(90, 120),
    "thumbnail": "https://imagex1.sx.cdn.live/images/pinporn/2014/08/26/7637609.jpg?width=300",
    "title"    : "Sexy Ecchi Girls 166",
    "type"     : "picture",
    "uploader" : "mangazeta",
    "url"      : "https://imagex1.sx.cdn.live/images/pinporn/2014/08/26/7637609.jpg",
    "tags": [
        "ecchi",
        "ecchi-girls",
        "Hot",
        "sexy-ecchi",
    ],
},

{
    "#url"     : "https://www.sex.com/en/pics/612398",
    "#comment" : "picture",
    "#category": ("", "sexcom", "pin"),
    "#class"   : sexcom.SexcomPinExtractor,
    "#results" : "https://imagex1.sx.cdn.live/images/pinporn/2014/08/26/7637609.jpg",

    "date"     : "dt:2014-08-26 00:00:00",
    "date_url" : "dt:2014-08-26 00:00:00",
    "extension": "jpg",
    "filename" : "7637609",
    "pin_id"   : 612398,
    "tags"     : ["Hot"],
    "title"    : "Sexy Ecchi Girls 166",
    "type"     : "picture",
},

{
    "#url"     : "https://www.sex.com/pin/55435122-ecchi/",
    "#comment" : "gif (legacy URL)",
    "#category": ("", "sexcom", "pin"),
    "#class"   : sexcom.SexcomPinExtractor,
    "#results"     : "https://imagex1.sx.cdn.live/images/pinporn/2017/12/07/18760842.gif",
    "#sha1_content": "176cc63fa05182cb0438c648230c0f324a5965fe",

    "date"     : "dt:2017-12-07 00:00:00",
    "date_url" : "dt:2017-12-07 00:00:00",
    "extension": "gif",
    "filename" : "18760842",
    "pin_id"   : 209061,
    "title"    : "Ecchi",
    "type"     : "gif",
    "url"      : "https://imagex1.sx.cdn.live/images/pinporn/2017/12/07/18760842.gif",
    "_fallback": ("https://imagex1.sx.cdn.live/images/pinporn/2017/12/07/18760842.webp",),
    "tags"     : [
        "Big Tits",
        "Hentai",
    ],
},

{
    "#url"     : "https://www.sex.com/en/gifs/209061",
    "#comment" : "gif",
    "#category": ("", "sexcom", "pin"),
    "#class"   : sexcom.SexcomPinExtractor,
    "#options" : {"gifs": False},
    "#results"     : "https://imagex1.sx.cdn.live/images/pinporn/2017/12/07/18760842.webp",
    "#sha1_content": "d5d58fbb92f87be49a37d29d82687c9efa7f796f",

    "date"     : "dt:2017-12-07 00:00:00",
    "date_url" : "dt:2017-12-07 00:00:00",
    "extension": "webp",
    "filename" : "18760842",
    "pin_id"   : 209061,
    "title"    : "Ecchi",
    "type"     : "gif",
    "url"      : "https://imagex1.sx.cdn.live/images/pinporn/2017/12/07/18760842.webp",
    "tags"     : [
        "Big Tits",
        "Hentai",
    ],
},

{
    "#url"     : "https://www.sex.com/pin/55748341/",
    "#comment" : "video (legacy URL)",
    "#category": ("", "sexcom", "pin"),
    "#class"   : sexcom.SexcomPinExtractor,
    "#skip"    : "gone",
    "#results"     : "https://video1.sx.cdn.live/videos/pinporn/2018/02/10/776229_hd.mp4",
    "#sha1_content": "e1a5834869163e2c4d1ca2677f5b7b367cf8cfff",

    "comments" : range(0, 5),
    "date"     : "dt:2018-02-10 14:58:55",
    "date_url" : "dt:2018-02-10 00:00:00",
    "extension": "mp4",
    "filename" : "776229_hd",
    "likes"    : range(30, 50),
    "pin_id"   : 55748341,
    "repins"   : range(10, 20),
    "thumbnail": "https://imagex1.sx.cdn.live/images/pinporn/2018/02/10/19082009.jpg?width=300",
    "title"    : "Pin #55748341",
    "type"     : "video",
    "uploader" : "Vinsein",
    "url"      : "https://video1.sx.cdn.live/videos/pinporn/2018/02/10/776229_hd.mp4",
    "tags": [
        "Hentai",
    ],
},

{
    "#url"     : "https://www.sex.com/en/videos/680933",
    "#comment" : "video",
    "#category": ("", "sexcom", "pin"),
    "#class"   : sexcom.SexcomPinExtractor,
    "#results" : "ytdl:https://videos.sex.com/680933/video.m3u8",

    "extension": "mp4",
    "pin_id"   : 680933,
    "title"    : "Underwater Big Boobs Kristy with Small Boobs Petra",
    "type"     : "video",
    "url"      : "ytdl:https://videos.sex.com/680933/video.m3u8",
    "tags"     : [
        "Babe",
        "Beach",
        "Big Boobs",
        "Bikini",
        "Brunette",
        "Brunette Babe",
        "Girlfriend",
        "Natural Tits",
        "Nude",
        "Pool",
        "Poolside",
        "Public Sex",
        "Russian",
        "Shower",
        "Small Boobs",
        "Swimming",
        "Swimming Pool",
        "Tight Pussy",
        "Underwater",
        "With",
        "Young",
    ],
},

{
    "#url"     : "https://www.sex.com/pin/55847384-very-nicely-animated/",
    "#comment" : "pornhub embed (404 gone)",
    "#category": ("", "sexcom", "pin"),
    "#class"   : sexcom.SexcomPinExtractor,
},

{
    "#url"     : "https://www.sex.com/pin/21241874/#related",
    "#category": ("", "sexcom", "related-pin"),
    "#class"   : sexcom.SexcomRelatedPinExtractor,
    "#count"   : ">= 20",
},

{
    "#url"     : "https://www.sex.com/user/sirjuan79/pins/",
    "#category": ("", "sexcom", "pins"),
    "#class"   : sexcom.SexcomPinsExtractor,
    "#count"   : ">= 4",
},

{
    "#url"     : "https://www.sex.com/user/sirjuan79/likes/",
    "#category": ("", "sexcom", "likes"),
    "#class"   : sexcom.SexcomLikesExtractor,
    "#range"   : "1-30",
    "#count"   : ">= 25",
},

{
    "#url"     : "https://www.sex.com/user/ronin17/exciting-hentai/",
    "#category": ("", "sexcom", "board"),
    "#class"   : sexcom.SexcomBoardExtractor,
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.sex.com/search/pics?query=ecchi",
    "#category": ("", "sexcom", "search"),
    "#class"   : sexcom.SexcomSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.sex.com/videos/hentai/",
    "#category": ("", "sexcom", "search"),
    "#class"   : sexcom.SexcomSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.sex.com/pics/?sort=popular&sub=all&page=1",
    "#category": ("", "sexcom", "search"),
    "#class"   : sexcom.SexcomSearchExtractor,
},

{
    "#url"     : "https://www.sex.com/en/gifs?search=bed",
    "#class"   : sexcom.SexcomSearchExtractor,
    "#pattern" : r"https://imagex1.sx.cdn.live/images/pinporn/\d\d\d\d/\d\d/\d\d/\d+\.gif",
    "#range"   : "1-50",
    "#count"   : 50,

    "date"       : "type:datetime",
    "date_url"   : "type:datetime",
    "extension"  : "gif",
    "externalId" : int,
    "filename"   : str,
    "width"      : range(10, 1000),
    "height"     : range(10, 1000),
    "pin_id"     : int,
    "search"     : {
        "order"             : "likeCount",
        "search"            : "bed",
        "sexual-orientation": "straight",
        "type"              : "gif",
    },
    "title"      : str,
    "type"       : "gif",
    "uri"        : str,
    "url"        : str,
},

{
    "#url"  : "https://www.sex.com/feed/",
    "#class": sexcom.SexcomFeedExtractor,
},

)
