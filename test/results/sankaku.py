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
    "#url"     : "https://sankaku.app/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options"     : {"tags": True},
    "#sha1_content": "5e255713cbf0a8e0801dc423563c34d896bb9229",

    "tags_artist"   : ["bonocho"],
    "tags_studio"   : ["dc_comics"],
    "tags_medium"   : list,
    "tags_copyright": list,
    "tags_character": list,
    "tags_general"  : list,
},

{
    "#url"     : "https://sankaku.app/post/show/21418978",
    "#comment" : "'contentious_content'",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/data/13/3c/133cda3bfde249c504284493903fb985\.jpg",
},

{
    "#url"     : "https://sankaku.app/post/show/20758561",
    "#comment" : "empty tags (#1617)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"tags": True},
    "#count"   : 1,

    "tags"        : list,
    "tags_general": [
        "key(mangaka)",
        "key(mangaka)",
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
