# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tumblr
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "http://demo.tumblr.com/",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#options" : {"posts": "photo"},
    "#pattern" : r"https://\d+\.media\.tumblr\.com/tumblr_[^/_]+_\d+\.jpg",
    "#count"   : 1,
},

{
    "#url"     : "http://demo.tumblr.com/",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#options" : {
        "posts"   : "all",
        "external": True,
    },
    "#pattern" : r"https?://(?:$|\d+\.media\.tumblr\.com/.+\.(jpg|png|gif|mp3|mp4)|v?a\.(media\.)?tumblr\.com/tumblr_\w+)",
    "#count"   : 27,
},

{
    "#url"     : "https://mikf123-hidden.tumblr.com/",
    "#comment" : "dashboard-only",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#options"  : {"access-token": None},
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://mikf123-hidden.tumblr.com/",
    "#comment" : "dashboard-only",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#count"   : 2,

    "tags": [
        "test",
        "hidden",
    ],
},

{
    "#url"     : "https://mikf123-private.tumblr.com/",
    "#comment" : "password protected",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#count"   : 2,

    "tags": [
        "test",
        "private",
    ],
},

{
    "#url"     : "https://mikf123-private-hidden.tumblr.com/",
    "#comment" : "dashboard-only & password protected",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#count"   : 2,

    "tags": [
        "test",
        "private",
        "hidden",
    ],
},

{
    "#url"     : "https://mikf123.tumblr.com/",
    "#comment" : "date-min/-max/-format (#337)",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#options" : {
        "date-min"   : "201804",
        "date-max"   : "201805",
        "date-format": "%Y%m",
    },
    "#count"   : 4,
},

{
    "#url"     : "https://donttrustthetits.tumblr.com/",
    "#comment" : "pagination with 'date-max' (#2191) and 'api-key'",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
    "#options" : {
        "access-token": None,
        "original"    : False,
        "date-max"    : "2015-04-25T00:00:00",
        "date-min"    : "2015-04-01T00:00:00",
    },
    "#count"   : 192,
},

{
    "#url"     : "https://demo.tumblr.com/page/2",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
},

{
    "#url"     : "https://demo.tumblr.com/archive",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
},

{
    "#url"     : "tumblr:http://www.b-authentique.com/",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
},

{
    "#url"     : "tumblr:www.b-authentique.com",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
},

{
    "#url"     : "https://www.tumblr.com/blog/view/smarties-art",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
},

{
    "#url"     : "https://www.tumblr.com/blog/smarties-art",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
},

{
    "#url"     : "https://www.tumblr.com/smarties-art",
    "#category": ("", "tumblr", "user"),
    "#class"   : tumblr.TumblrUserExtractor,
},

{
    "#url"     : "http://demo.tumblr.com/post/459265350",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#pattern" : r"https://\d+\.media\.tumblr\.com/tumblr_[^/_]+_1280.jpg",
    "#count"   : 1,
},

{
    "#url"     : "https://mikf123.tumblr.com/post/167770226574/text-post",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://mikf123.tumblr.com/post/181022561719/quote-post",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://mikf123.tumblr.com/post/167623351559/link-post",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://mikf123.tumblr.com/post/167633596145/video-post",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://mikf123.tumblr.com/post/167770026604/audio-post",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://mikf123.tumblr.com/post/172687798174/photo-post",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://mikf123.tumblr.com/post/181022380064/chat-post",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://kichatundk.tumblr.com/post/654953419288821760",
    "#comment" : "high-quality images (#1846)",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#count"       : 2,
    "#sha1_content": "d6fcc7b6f750d835d55c7f31fa3b63be26c9f89b",
},

{
    "#url"     : "https://hameru-is-cool.tumblr.com/post/639261855227002880",
    "#comment" : "high-quality images (#1344)",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#exception"   : exception.NotFoundError,
    "#count"       : 2,
    "#sha1_content": "6bc19a42787e46e1bba2ef4aeef5ca28fcd3cd34",
},

{
    "#url"     : "https://k-eke.tumblr.com/post/185341184856",
    "#comment" : "wrong extension returned by api (#3095)",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#options"     : {"retries": 0},
    "#urls"        : "https://64.media.tumblr.com/5e9d760aba24c65beaf0e72de5aae4dd/tumblr_psj5yaqV871t1ig6no1_1280.gif",
    "#sha1_content": "3508d894b6cc25e364d182a8e1ff370d706965fb",
},

{
    "#url"     : "https://mikf123.tumblr.com/image/689860196535762944",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#pattern" : r"^https://\d+\.media\.tumblr\.com/134791621559a79793563b636b5fe2c6/8f1131551cef6e74-bc/s99999x99999/188cf9b8915b0d0911c6c743d152fc62e8f38491\.png$",
},

{
    "#url"     : "http://ziemniax.tumblr.com/post/109697912859/",
    "#comment" : "HTML response (#297)",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "http://demo.tumblr.com/image/459265350",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
},

{
    "#url"     : "https://www.tumblr.com/blog/view/smarties-art/686047436641353728",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
},

{
    "#url"     : "https://www.tumblr.com/blog/smarties-art/686047436641353728",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
},

{
    "#url"     : "https://www.tumblr.com/smarties-art/686047436641353728",
    "#category": ("", "tumblr", "post"),
    "#class"   : tumblr.TumblrPostExtractor,
},

{
    "#url"     : "http://demo.tumblr.com/tagged/Times%20Square",
    "#category": ("", "tumblr", "tag"),
    "#class"   : tumblr.TumblrTagExtractor,
    "#pattern" : r"https://\d+\.media\.tumblr\.com/tumblr_[^/_]+_1280.jpg",
    "#count"   : 1,
},

{
    "#url"     : "https://www.tumblr.com/blog/view/smarties-art/tagged/undertale",
    "#category": ("", "tumblr", "tag"),
    "#class"   : tumblr.TumblrTagExtractor,
},

{
    "#url"     : "https://www.tumblr.com/blog/smarties-art/tagged/undertale",
    "#category": ("", "tumblr", "tag"),
    "#class"   : tumblr.TumblrTagExtractor,
},

{
    "#url"     : "https://www.tumblr.com/smarties-art/tagged/undertale",
    "#category": ("", "tumblr", "tag"),
    "#class"   : tumblr.TumblrTagExtractor,
},

{
    "#url"     : "https://mikf123.tumblr.com/day/2018/01/05",
    "#category": ("", "tumblr", "day"),
    "#class"   : tumblr.TumblrDayExtractor,
    "#pattern" : r"https://64\.media\.tumblr\.com/1a2be8c63f1df58abd2622861696c72a/tumblr_ozm9nqst9t1wgha4yo1_1280\.jpg",
    "#count"   : 1,

    "id": 169341068404,
},

{
    "#url"     : "https://www.tumblr.com/blog/view/mikf123/day/2018/01/05",
    "#category": ("", "tumblr", "day"),
    "#class"   : tumblr.TumblrDayExtractor,
},

{
    "#url"     : "https://www.tumblr.com/blog/mikf123/day/2018/01/05",
    "#category": ("", "tumblr", "day"),
    "#class"   : tumblr.TumblrDayExtractor,
},

{
    "#url"     : "https://www.tumblr.com/mikf123/day/2018/01/05",
    "#category": ("", "tumblr", "day"),
    "#class"   : tumblr.TumblrDayExtractor,
},

{
    "#url"     : "http://mikf123.tumblr.com/likes",
    "#category": ("", "tumblr", "likes"),
    "#class"   : tumblr.TumblrLikesExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://www.tumblr.com/blog/view/mikf123/likes",
    "#category": ("", "tumblr", "likes"),
    "#class"   : tumblr.TumblrLikesExtractor,
},

{
    "#url"     : "https://www.tumblr.com/blog/mikf123/likes",
    "#category": ("", "tumblr", "likes"),
    "#class"   : tumblr.TumblrLikesExtractor,
},

{
    "#url"     : "https://www.tumblr.com/mikf123/likes",
    "#category": ("", "tumblr", "likes"),
    "#class"   : tumblr.TumblrLikesExtractor,
},

)
