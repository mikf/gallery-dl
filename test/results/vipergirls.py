# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vipergirls


__tests__ = (
{
    "#url"     : "https://vipergirls.to/threads/4328304-2011-05-28-Danica-Simply-Beautiful-x112-4500x3000",
    "#category": ("", "vipergirls", "thread"),
    "#class"   : vipergirls.VipergirlsThreadExtractor,
    "#count"   : 225,
    "#sha1_url": "3a127b2d4f61d538ac4ad5340a787ef9f0b05b1f",

    "count"       : {112, 113},
    "num"         : range(1, 113),
    "forum_title" : "Artistic Photo Sets (Archive)",
    "post_id"     : {"116038081", "42953564"},
    "post_num"    : {"1", "2"},
    "post_title"  : str,
    "thread_id"   : "4328304",
    "thread_title": "FemJoy 2011-05-28 Danica - Simply Beautiful [x112] 4500x3000",
},

{
    "#url"     : "https://vipergirls.to/threads/6858916-Karina/page4",
    "#category": ("", "vipergirls", "thread"),
    "#class"   : vipergirls.VipergirlsThreadExtractor,
    "#options" : {"order-posts": "asc"},
    "#count"   : 1279,
},

{
    "#url"     : "https://vipergirls.to/threads/4328304-2011-05-28-Danica-Simply-Beautiful-x112-4500x3000?highlight=foobar",
    "#category": ("", "vipergirls", "thread"),
    "#class"   : vipergirls.VipergirlsThreadExtractor,
},

{
    "#url"     : "https://vipergirls.to/threads/4328304?foo=bar",
    "#category": ("", "vipergirls", "thread"),
    "#class"   : vipergirls.VipergirlsThreadExtractor,
},

{
    "#url"     : "https://vipergirls.to/threads/4328304",
    "#category": ("", "vipergirls", "thread"),
    "#class"   : vipergirls.VipergirlsThreadExtractor,
},

{
    "#url"     : "https://vipergirls.to/threads/4328304-2011-05-28-Danica-Simply-Beautiful-x112-4500x3000?p=116038081&viewfull=1#post116038081",
    "#category": ("", "vipergirls", "post"),
    "#class"   : vipergirls.VipergirlsPostExtractor,
    "#pattern" : r"https://vipr\.im/\w{12}$",
    "#range"   : "2-113",
    "#count"   : 112,

    "count"       : 113,
    "num"         : range(2, 113),
    "post_id"     : "116038081",
    "post_num"    : "116038081",
    "post_title"  : "FemJoy Danica - Simply Beautiful (x112) 3000x4500",
    "thread_id"   : "4328304",
    "thread_title": "FemJoy 2011-05-28 Danica - Simply Beautiful [x112] 4500x3000",
},

)
