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
    "#url"     : "https://e621.net/post?tags=",
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
    "#results" : "https://static1.e621.net/data/63/0b/630b624cc581023ef9d26fd89d37a410.jpg",
    "#sha1_content": "66f46e96a893fba8e694c4e049b23c2acc9af462",

    "approver_id"     : None,
    "change_seq"      : 59815157,
    "comment_count"   : range(4, 8),
    "created_at"      : "iso:dt",
    "date"            : "dt:2007-02-17 19:02:32",
    "description"     : "",
    "duration"        : None,
    "extension"       : "jpg",
    "fav_count"       : range(200, 500),
    "filename"        : "630b624cc581023ef9d26fd89d37a410",
    "has_notes"       : False,
    "id"              : 535,
    "is_favorited"    : False,
    "locked_tags"     : [],
    "pools"           : [],
    "rating"          : "s",
    "sources"         : ["https://www.anry.ru"],
    "tags_artist"     : ["anry"],
    "tags_character"  : [],
    "tags_contributor": [],
    "tags_copyright"  : [],
    "tags_invalid"    : [],
    "tags_lore"       : [],
    "updated_at"      : "iso:dt",
    "uploader_id"     : 8,
    "uploader_name"   : "mellis",
    "tags"            : list,
    "tags_general"    : list,
    "tags_meta"       : [
        "1:1",
        "english_text",
    ],
    "tags_species"    : [
        "ambient_arthropod",
        "ambient_insect",
        "ambient_moth",
        "arthropod",
        "canid",
        "canine",
        "fennec_fox",
        "fox",
        "insect",
        "lepidopteran",
        "mammal",
        "moth",
        "true_fox",
    ],
    "file"            : {
        "ext"   : "jpg",
        "height": 900,
        "md5"   : "630b624cc581023ef9d26fd89d37a410",
        "size"  : 155108,
        "url"   : "https://static1.e621.net/data/63/0b/630b624cc581023ef9d26fd89d37a410.jpg",
        "width" : 900,
    },
    "flags"           : {
        "deleted"      : False,
        "flagged"      : False,
        "note_locked"  : False,
        "pending"      : False,
        "rating_locked": False,
        "status_locked": False,
    },
    "preview"         : {
        "alt"   : "https://static1.e621.net/data/preview/63/0b/630b624cc581023ef9d26fd89d37a410.webp",
        "height": 256,
        "url"   : "https://static1.e621.net/data/preview/63/0b/630b624cc581023ef9d26fd89d37a410.jpg",
        "width" : 256,
    },
    "relationships"   : {
        "children"    : [],
        "has_active_children": False,
        "has_children": False,
        "parent_id"   : None,
    },
    "sample"          : {
        "alt"       : "https://static1.e621.net/data/sample/63/0b/630b624cc581023ef9d26fd89d37a410.webp",
        "alternates": {},
        "has"       : True,
        "height"    : 850,
        "url"       : "https://static1.e621.net/data/sample/63/0b/630b624cc581023ef9d26fd89d37a410.jpg",
        "width"     : 850,
    },
    "score"           : {
        "down" : -8,
        "total": 134,
        "up"   : 141,
    },
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
[quote]h2.【web再録】ぷち・れじぇんず2
2015年の関西けもケット4で頒布した個人誌第2弾！
～行方不明になった親友のビクティニを救うべく怪しげな館に単身乗り込んだミュウ。
しかし彼女の前には強大な力を持つ館の主が立ちはだかる！果たして二人は無事脱出することができるのか！？～
 \n\
この頃の方が背景に力が入ってますねw
あとジャローダの顔の模様思いっきり間違ってますがそこはご愛嬌ということで…[/quote]

* "Little Legends":/pools/27971
* Little Legends 2
* "Little Legends 3":/pools/27481\
""",

            "id"          : 27492,
            "is_active"   : False,
            "name"        : "Little Legends 2",
            "post_count"  : 39,
            "post_ids"    : list,
            "updated_at"  : "2025-01-07T22:01:40.319-05:00",
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
    "#url"     : "https://e621.net/favorites?page=1&user_id=460755",
    "#category": ("E621", "e621", "favorite"),
    "#class"   : e621.E621FavoriteExtractor,
    "#pattern" : r"https://static\d.e621.net/data/../../[0-9a-f]+",
    "#count"   : 15,
},

{
    "#url"     : "https://e621.cc/posts?tags=rating:safe",
    "#category": ("E621", "e621", "tag"),
    "#class"   : e621.E621TagExtractor,
},

{
    "#url"     : "https://e621.cc/?tags=rating:safe",
    "#category": ("E621", "e621", "frontend"),
    "#class"   : e621.E621FrontendExtractor,
    "#results" : "https://e621.net/posts?tags=rating:safe",
},

{
    "#url"     : "https://e621.anthro.fr/?q=rating:safe",
    "#category": ("E621", "e621", "frontend"),
    "#class"   : e621.E621FrontendExtractor,
    "#results" : "https://e621.net/posts?tags=rating:safe",
},

{
    "#url"     : "https://e621.net/artists/54632",
    "#category": ("E621", "e621", "artist"),
    "#class"   : e621.E621ArtistExtractor,
    "#results" : "https://e621.net/posts?tags=emsibap",

    "created_at"    : "2021-05-01T11:28:56.483-04:00",
    "creator_id"    : 338533,
    "domains"       : [[
        "furaffinity.net",
        3,
    ]],
    "group_name"    : "",
    "id"            : 54632,
    "is_active"     : True,
    "is_locked"     : False,
    "linked_user_id": None,
    "name"          : "emsibap",
    "notes"         : None,
    "other_names"   : [],
    "updated_at"    : "2021-05-01T11:28:56.488-04:00",
    "urls"          : [{
        "artist_id"     : 54632,
        "created_at"    : "2021-05-01T11:28:56.486-04:00",
        "id"            : 217681,
        "is_active"     : True,
        "normalized_url": "http://www.furaffinity.net/user/emsibap/",
        "updated_at"    : "2021-05-01T11:28:56.486-04:00",
        "url"           : "https://www.furaffinity.net/user/emsibap",
    }],
},

{
    "#url"     : "https://e621.net/artists?search%5Bany_name_or_url_matches%5D=emsi",
    "#category": ("E621", "e621", "artist-search"),
    "#class"   : e621.E621ArtistSearchExtractor,
    "#results" : (
        "https://e621.net/posts?tags=loremsipsum",
        "https://e621.net/posts?tags=demsigma",
        "https://e621.net/posts?tags=emsibap",
        "https://e621.net/posts?tags=aluminemsiren",
    ),
},

)
