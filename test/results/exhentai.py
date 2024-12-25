# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import exhentai
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://exhentai.org/g/1200119/d55c44d3d0/",
    "#category": ("", "exhentai", "gallery"),
    "#class"   : exhentai.ExhentaiGalleryExtractor,
    "#options"     : {"original": False, "tags": True},
    "#sha1_content": [
        "2c68cff8a7ca540a78c36fdbf5fbae0260484f87",
        "e9891a4c017ed0bb734cd1efba5cd03f594d31ff",
    ],

    "cost"        : int,
    "date"        : "dt:2018-03-18 20:14:00",
    "eh_category" : "Non-H",
    "expunged"    : False,
    "favorites"   : r"re:^[12]\d$",
    "filecount"   : "4",
    "filesize"    : 1488978,
    "gid"         : 1200119,
    "height"      : int,
    "image_token" : r"re:[0-9a-f]{10}",
    "lang"        : "ja",
    "language"    : "Japanese",
    "parent"      : "",
    "rating"      : r"re:\d\.\d+",
    "size"        : int,
    "tags"        : [
        "parody:komi-san wa komyushou desu.",
        "character:shouko komi",
        "group:seventh lowlife",
        "other:sample",
    ],
    "tags_parody" : ["komi-san wa komyushou desu."],
    "tags_character": ["shouko komi"],
    "tags_group"  : ["seventh lowlife"],
    "tags_other"  : ["sample"],
    "thumb"       : "https://s.exhentai.org/t/ce/0a/ce0a5bcb583229a9b07c0f83bcb1630ab1350640-624622-736-1036-jpg_250.jpg",
    "title"       : "C93 [Seventh_Lowlife] Komi-san ha Tokidoki Daitan desu (Komi-san wa Komyushou desu) [Sample]",
    "title_jpn"   : "(C93) [Comiketjack (わ！)] 古見さんは、時々大胆です。 (古見さんは、コミュ症です。) [見本]",
    "token"       : "d55c44d3d0",
    "torrentcount": "0",
    "uploader"    : "klorpa",
    "width"       : int,
},

{
    "#url"     : "https://exhentai.org/g/960461/4f0e369d82/",
    "#category": ("", "exhentai", "gallery"),
    "#class"   : exhentai.ExhentaiGalleryExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "http://exhentai.org/g/962698/7f02358e00/",
    "#category": ("", "exhentai", "gallery"),
    "#class"   : exhentai.ExhentaiGalleryExtractor,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://exhentai.org/s/f68367b4c8/1200119-3",
    "#category": ("", "exhentai", "gallery"),
    "#class"   : exhentai.ExhentaiGalleryExtractor,
    "#options" : {"original": False},
    "#count"   : 2,
},

{
    "#url"     : "https://e-hentai.org/s/f68367b4c8/1200119-3",
    "#category": ("", "exhentai", "gallery"),
    "#class"   : exhentai.ExhentaiGalleryExtractor,
    "#options" : {"original": False},
    "#count"   : 2,
},

{
    "#url"     : "https://g.e-hentai.org/g/1200119/d55c44d3d0/",
    "#category": ("", "exhentai", "gallery"),
    "#class"   : exhentai.ExhentaiGalleryExtractor,
},

{
    "#url"     : "https://e-hentai.org/?f_search=touhou",
    "#category": ("", "exhentai", "search"),
    "#class"   : exhentai.ExhentaiSearchExtractor,
},

{
    "#url"     : "https://exhentai.org/?f_cats=767&f_search=touhou",
    "#category": ("", "exhentai", "search"),
    "#class"   : exhentai.ExhentaiSearchExtractor,
},

{
    "#url"     : "https://exhentai.org/tag/parody:touhou+project",
    "#category": ("", "exhentai", "search"),
    "#class"   : exhentai.ExhentaiSearchExtractor,
},

{
    "#url"     : "https://exhentai.org/?f_doujinshi=0&f_manga=0&f_artistcg=0&f_gamecg=0&f_western=0&f_non-h=1&f_imageset=0&f_cosplay=0&f_asianporn=0&f_misc=0&f_search=touhou&f_apply=Apply+Filter",
    "#category": ("", "exhentai", "search"),
    "#class"   : exhentai.ExhentaiSearchExtractor,
    "#pattern" : exhentai.ExhentaiGalleryExtractor.pattern,
    "#auth"    : True,
    "#range"   : "1-30",
    "#count"   : 30,

    "gallery_id"   : int,
    "gallery_token": r"re:^[0-9a-f]{10}$",
},

{
    "#url"     : "https://e-hentai.org/favorites.php",
    "#category": ("", "exhentai", "favorite"),
    "#class"   : exhentai.ExhentaiFavoriteExtractor,
    "#auth"    : True,
    "#urls"    : "https://e-hentai.org/g/1200119/d55c44d3d0/",
},

{
    "#url"     : "https://exhentai.org/favorites.php?favcat=1&f_search=touhou&f_apply=Search+Favorites",
    "#category": ("", "exhentai", "favorite"),
    "#class"   : exhentai.ExhentaiFavoriteExtractor,
},

)
