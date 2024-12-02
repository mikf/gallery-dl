# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import e621


__tests__ = (
{
    "#url"     : "https://e621.net/posts?tags=anry",
    "#category": ("E621", "e621", "tag"),
    "#class"   : e621.E621TagExtractor,
    "#options"     : {"metadata": True},
    "#sha1_url"    : "8021e5ea28d47c474c1ffc9bd44863c4d45700ba",
    "#sha1_content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
},

{
    "#url"     : "https://e621.net/post/index/1/anry",
    "#category": ("E621", "e621", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e621.net/post?tags=anry",
    "#category": ("E621", "e621", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e621.net/pools/73",
    "#category": ("E621", "e621", "pool"),
    "#class"   : e621.E621PoolExtractor,
    "#sha1_url"    : "1bd09a72715286a79eea3b7f09f51b3493eb579a",
    "#sha1_content": "91abe5d5334425d9787811d7f06d34c77974cd22",
},

{
    "#url"     : "https://e621.net/pool/show/73",
    "#category": ("E621", "e621", "pool"),
    "#class"   : e621.E621PoolExtractor,
},

{
    "#url"     : "https://e621.net/posts/535",
    "#category": ("E621", "e621", "post"),
    "#class"   : e621.E621PostExtractor,
    "#sha1_url"    : "f7f78b44c9b88f8f09caac080adc8d6d9fdaa529",
    "#sha1_content": "66f46e96a893fba8e694c4e049b23c2acc9af462",

    "date": "dt:2007-02-17 19:02:32",
},

{
    "#url"     : "https://e621.net/posts/3181052",
    "#category": ("E621", "e621", "post"),
    "#class"   : e621.E621PostExtractor,
    "#options" : {"metadata": "notes,pools"},
    "#pattern" : r"https://static\d\.e621\.net/data/c6/8c/c68cca0643890b615f75fb2719589bff\.png",

    "notes": [
        {
            "body"        : "Little Legends 2",
            "created_at"  : "2022-05-16T13:58:38.877-04:00",
            "creator_id"  : 517450,
            "creator_name": "EeveeCuddler69",
            "height"      : 475,
            "id"          : 321296,
            "is_active"   : True,
            "post_id"     : 3181052,
            "updated_at"  : "2022-05-16T13:59:02.050-04:00",
            "version"     : 3,
            "width"       : 809,
            "x"           : 83,
            "y"           : 117,
        },
    ],
    "pools": [
        {
            "category"    : "series",
            "created_at"  : "2022-02-17T00:29:22.669-05:00",
            "creator_id"  : 1077440,
            "creator_name": "Yeetus90",
            "description" : """\
* "Little Legends":/pools/27971\r
* Little Legends 2\r
* "Little Legends 3":/pools/27481\
""",
            "id"          : 27492,
            "is_active"   : False,
            "name"        : "Little Legends 2",
            "post_count"  : 39,
            "post_ids"    : list,
            "updated_at"  : "2022-03-27T06:30:03.382-04:00",
        },
    ],
},

{
    "#url"     : "https://e621.net/post/show/535",
    "#category": ("E621", "e621", "post"),
    "#class"   : e621.E621PostExtractor,
},

{
    "#url"     : "https://e621.net/explore/posts/popular",
    "#category": ("E621", "e621", "popular"),
    "#class"   : e621.E621PopularExtractor,
},

{
    "#url"     : "https://e621.net/explore/posts/popular?date=2019-06-01&scale=month",
    "#category": ("E621", "e621", "popular"),
    "#class"   : e621.E621PopularExtractor,
    "#pattern" : r"https://static\d.e621.net/data/../../[0-9a-f]+",
    "#count"   : ">= 70",
},

{
    "#url"     : "https://e621.net/favorites",
    "#category": ("E621", "e621", "favorite"),
    "#class"   : e621.E621FavoriteExtractor,
},

{
    "#url"     : "https://e621.net/favorites?page=2&user_id=53275",
    "#category": ("E621", "e621", "favorite"),
    "#class"   : e621.E621FavoriteExtractor,
    "#pattern" : r"https://static\d.e621.net/data/../../[0-9a-f]+",
    "#count"   : "> 260",
},

)
