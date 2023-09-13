# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import livedoor


__tests__ = (
{
    "#url"     : "http://blog.livedoor.jp/zatsu_ke/",
    "#category": ("", "livedoor", "blog"),
    "#class"   : livedoor.LivedoorBlogExtractor,
    "#pattern" : r"https?://livedoor.blogimg.jp/\w+/imgs/\w/\w/\w+\.\w+",
    "#range"   : "1-50",
    "#count"   : 50,
    "#archive" : False,

    "post"    : {
        "categories" : tuple,
        "date"       : "type:datetime",
        "description": str,
        "id"         : int,
        "tags"       : list,
        "title"      : str,
        "user"       : "zatsu_ke",
    },
    "filename": str,
    "hash"    : r"re:\w{4,}",
    "num"     : int,
},

{
    "#url"     : "http://blog.livedoor.jp/uotapo/",
    "#category": ("", "livedoor", "blog"),
    "#class"   : livedoor.LivedoorBlogExtractor,
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : "http://blog.livedoor.jp/zatsu_ke/archives/51493859.html",
    "#category": ("", "livedoor", "post"),
    "#class"   : livedoor.LivedoorPostExtractor,
    "#sha1_url"     : "9ca3bbba62722c8155be79ad7fc47be409e4a7a2",
    "#sha1_metadata": "1f5b558492e0734f638b760f70bfc0b65c5a97b9",
},

{
    "#url"     : "http://blog.livedoor.jp/amaumauma/archives/7835811.html",
    "#category": ("", "livedoor", "post"),
    "#class"   : livedoor.LivedoorPostExtractor,
    "#sha1_url"     : "204bbd6a9db4969c50e0923855aeede04f2e4a62",
    "#sha1_metadata": "05821c7141360e6057ef2d382b046f28326a799d",
},

{
    "#url"     : "http://blog.livedoor.jp/uotapo/archives/1050616939.html",
    "#category": ("", "livedoor", "post"),
    "#class"   : livedoor.LivedoorPostExtractor,
    "#sha1_url"     : "4b5ab144b7309eb870d9c08f8853d1abee9946d2",
    "#sha1_metadata": "84fbf6e4eef16675013d6333039a7cfcb22c2d50",
},

)
