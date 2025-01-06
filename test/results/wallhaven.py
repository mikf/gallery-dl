# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wallhaven


__tests__ = (
{
    "#url"     : "https://wallhaven.cc/search?q=touhou",
    "#category": ("", "wallhaven", "search"),
    "#class"   : wallhaven.WallhavenSearchExtractor,
    "#pattern" : r"https://w\.wallhaven\.cc/full/\w\w/wallhaven-\w+\.\w+",
    "#range"   : "1-10",

    "search": {
        "q"     : "touhou",
        "tags"  : "touhou",
        "tag_id": 0,
    },
},

{
    "#url"     : "https://wallhaven.cc/search?q=id%3A87&categories=111&purity=100&sorting=date_added&order=asc&page=3",
    "#category": ("", "wallhaven", "search"),
    "#class"   : wallhaven.WallhavenSearchExtractor,
    "#pattern" : r"https://w\.wallhaven\.cc/full/\w\w/wallhaven-\w+\.\w+",
    "#count"   : "<= 30",

    "search": {
        "categories": "111",
        "order"     : "asc",
        "page"      : "3",
        "purity"    : "100",
        "sorting"   : "date_added",
        "q"         : "id:87",
        "tags"      : "Fujibayashi Kyou",
        "tag_id"    : 87,
    },
},

{
    "#url"     : "https://wallhaven.cc/user/AksumkA/favorites/74",
    "#category": ("", "wallhaven", "collection"),
    "#class"   : wallhaven.WallhavenCollectionExtractor,
    "#count"   : ">= 50",
},

{
    "#url"     : "https://wallhaven.cc/user/AksumkA/",
    "#category": ("", "wallhaven", "user"),
    "#class"   : wallhaven.WallhavenUserExtractor,
},

{
    "#url"     : "https://wallhaven.cc/user/AksumkA/favorites",
    "#category": ("", "wallhaven", "collections"),
    "#class"   : wallhaven.WallhavenCollectionsExtractor,
    "#pattern" : wallhaven.WallhavenCollectionExtractor.pattern,
    "#count"   : 4,
},

{
    "#url"     : "https://wallhaven.cc/user/AksumkA/uploads",
    "#category": ("", "wallhaven", "uploads"),
    "#class"   : wallhaven.WallhavenUploadsExtractor,
    "#pattern" : r"https://[^.]+\.wallhaven\.cc/full/\w\w/wallhaven-\w+\.\w+",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://wallhaven.cc/w/01w334",
    "#category": ("", "wallhaven", "image"),
    "#class"   : wallhaven.WallhavenImageExtractor,
    "#pattern"     : r"https://[^.]+\.wallhaven\.cc/full/01/wallhaven-01w334\.jpg",
    "#sha1_content": "497212679383a465da1e35bd75873240435085a2",

    "id"         : "01w334",
    "width"      : 1920,
    "height"     : 1200,
    "resolution" : "1920x1200",
    "ratio"      : "1.6",
    "colors"     : list,
    "tags"       : list,
    "file_size"  : 278799,
    "file_type"  : "image/jpeg",
    "purity"     : "sfw",
    "short_url"  : "https://whvn.cc/01w334",
    "source"     : str,
    "uploader"   : {
        "group"   : "Owner/Developer",
        "username": "AksumkA",
    },
    "date"       : "dt:2014-08-31 06:17:19",
    "wh_category": "anime",
    "views"      : int,
    "favorites"  : int,
},

{
    "#url"     : "https://wallhaven.cc/w/dge6v3",
    "#comment" : "NSFW",
    "#category": ("", "wallhaven", "image"),
    "#class"   : wallhaven.WallhavenImageExtractor,
    "#sha1_url": "e4b802e70483f659d790ad5d0bd316245badf2ec",
},

{
    "#url"     : "https://whvn.cc/01w334",
    "#category": ("", "wallhaven", "image"),
    "#class"   : wallhaven.WallhavenImageExtractor,
},

{
    "#url"     : "https://w.wallhaven.cc/full/01/wallhaven-01w334.jpg",
    "#category": ("", "wallhaven", "image"),
    "#class"   : wallhaven.WallhavenImageExtractor,
},

)
