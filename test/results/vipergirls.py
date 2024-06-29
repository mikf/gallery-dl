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
    "#sha1_url": "0d75cb42777f5bebc0d284d1d38cb90c750c61d9",
},

{
    "#url"     : "https://vipergirls.to/threads/6858916-Karina/page4",
    "#category": ("", "vipergirls", "thread"),
    "#class"   : vipergirls.VipergirlsThreadExtractor,
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

    "id"        : "116038081",
    "imagecount": "113",
    "number"    : "116038081",
    "thread_id" : "4328304",
    "title"     : "FemJoy Danica - Simply Beautiful (x112) 3000x4500",
},

)
