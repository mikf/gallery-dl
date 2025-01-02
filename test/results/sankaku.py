# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import sankaku
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://sankaku.app/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}/[0-9a-f]{32}\.\w+\?e=\d+&(expires=\d+&)?m=[^&#]+",
    "#count"   : 5,
},

{
    "#url"     : "https://www.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://beta.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://black.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://white.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://sankaku.app/ja?tags=order%3Apopularity",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://sankaku.app/no/?tags=order%3Apopularity",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/posts?tags=TAG",
    "#comment" : "'/posts' in tag search URL (#4740)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/ja/posts/?tags=あえいおう",
    "#comment" : "'/posts' in tag search URL (#4740)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=bonocho+a+b+c+d",
    "#comment" : "error on five or more tags",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
    "#options"  : {"username": None},
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=marie_rose&page=98&next=3874906&commit=Search",
    "#comment" : "match arbitrary query parameters",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=date:2023-03-20",
    "#comment" : "'date:' tags (#1790)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
    "#range"   : "1",
    "#count"   : 1,
},

{
    "#url"     : "https://sankaku.app/books/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
    "#count"   : 5,
},

{
    "#url"     : "https://www.sankakucomplex.com/books/8YEa7EERmD0",
    "#comment" : "alphanumeric book/pool ID (#6757)",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
    "#count"   : 5,
},

{
    "#url"     : "https://www.sankakucomplex.com/books/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://beta.sankakucomplex.com/books/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/pool/show/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/pools/show/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://sankaku.app/posts/y0abGlDOr2o",
    "#comment" : "extended tag categories; alphanumeric ID (#5073)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options"     : {
        "tags"     : True,
        "notes"    : True,
        "id-format": "alphanumeric",
    },
    "#sha1_content": "5e255713cbf0a8e0801dc423563c34d896bb9229",

    "id": "y0abGlDOr2o",
    "notes": (),
    "tags_artist": [
        "bonocho",
    ],
    "tags_character": [
        "batman",
        "letty_whiterock",
        "bruce_wayne",
        "the_joker",
        "heath_ledger",
    ],
    "tags_copyright": [
        "batman_(series)",
        "the_dark_knight",
    ],
    "tags_studio": [
        "dc_comics",
    ],
    "tags_general": list,
},

{
    "#url"     : "https://sankaku.app/posts/VAr2mjLJ2av",
    "#comment" : "notes (#5073)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"notes": True},

    "notes": [
        {
            "body"      : "A lonely person, is a lonely person, because he or she is lonely.",
            "created_at": 1643733759,
            "creator_id": 1370766,
            "height"    : 871,
            "id"        : 1832643,
            "is_active" : True,
            "post_id"   : 23688624,
            "updated_at": 1643733759,
            "width"     : 108,
            "x"         : 703,
            "y"         : 83,
        },
    ],
},

{
    "#url"     : "https://sankaku.app/post/show/360451",
    "#comment" : "legacy post URL",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/data/ac/8e/ac8e3b92ea328ce9cf7211e69c905bf9\.jpg\?e=.+",

    "id": 360451,
},

{
    "#url"     : "https://sankaku.app/post/show/21418978",
    "#comment" : "'contentious_content'",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#auth"    : True,
    "#pattern" : r"https://s\.sankakucomplex\.com/data/13/3c/133cda3bfde249c504284493903fb985\.jpg",
},

{
    "#url"     : "https://sankaku.app/post/show/20758561",
    "#comment" : "empty tags (#1617)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"tags": True},
    "#count"   : 1,

    "id"          : 20758561,
    "tags"        : list,
    "tags_general": [
        "key(mangaka)",
        "key(mangaka)",
        "english_language",
        "english_language",
        "high_resolution",
        "tagme",
        "very_high_resolution",
        "large_filesize",
    ],
},

{
    "#url"     : "https://chan.sankakucomplex.com/post/show/f8ba89043078f0e4be2d9c46550b840a",
    "#comment" : "md5 hexdigest instead of ID (#3952)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/data/f8/ba/f8ba89043078f0e4be2d9c46550b840a\.jpg",
    "#count"   : 1,

    "id" : 33195194,
    "md5": "f8ba89043078f0e4be2d9c46550b840a",
},

{
    "#url"     : "https://chan.sankakucomplex.com/posts/f8ba89043078f0e4be2d9c46550b840a",
    "#comment" : "/posts/ instead of /post/show/ (#4688)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/data/f8/ba/f8ba89043078f0e4be2d9c46550b840a\.jpg",
    "#count"   : 1,

    "id" : 33195194,
    "md5": "f8ba89043078f0e4be2d9c46550b840a",
},

{
    "#url"     : "https://chan.sankakucomplex.com/en/posts/show/ac8e3b92ea328ce9cf7211e69c905bf9",
    "#comment" : "/en/posts/show/HEX",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,

    "id" : 360451,
    "md5": "ac8e3b92ea328ce9cf7211e69c905bf9",
},

{
    "#url"     : "https://chan.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/ja/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://beta.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://white.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://black.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://sankaku.app/books?tags=aiue_oka",
    "#category": ("booru", "sankaku", "books"),
    "#class"   : sankaku.SankakuBooksExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://beta.sankakucomplex.com/books?tags=aiue_oka",
    "#category": ("booru", "sankaku", "books"),
    "#class"   : sankaku.SankakuBooksExtractor,
},

)
