# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xasiat


__tests__ = (
{
    "#url"    : "https://www.xasiat.com/albums/28156/photobook-2024-12-09-bomb/",
    "#class"  : xasiat.XasiatAlbumExtractor,
    "#pattern": r"https://www.xasiat.com/get_image/2/\w{32}/sources/28000/28156/\d+.jpg/",
    "#count"  : 61,

    "title"         : "[Photobook] 2024.12.09 白濱美兎『忘れられない恋の味』BOMBデジタル写真集",
    "album_category": "JAV & AV Models",
    "album_id"      : 28156,
    "album_url"     : "https://www.xasiat.com/albums/28156/photobook-2024-12-09-bomb/",
    "count"         : 61,
    "num"           : range(1, 61),
    "extension"     : "jpg",
    "filename"      : r"re:\d+",
    "model"         : [],
    "tags"          : [
        "BOMB Photobook",
        "Photobook",
    ],
},

{
    "#url"  : "https://www.xasiat.com/ja/albums/28155/cosplay1813/",
    "#class": xasiat.XasiatAlbumExtractor,
    "#count": 40,

    "title"         : "[Cosplay] 喜欢爱理吗 - 早濑优香",
    "album_category": "グラビアアイドル",
    "album_id"      : 28155,
    "album_url"     : "https://www.xasiat.com/ja/albums/28155/cosplay1813/",
    "count"         : 40,
    "num"           : range(1, 40),
    "model"         : [],
    "tags"          : ["コスプレ"],
},

{
    "#url"  : "https://www.xasiat.com/fr/albums/23354/friday-impact-beauty-col-1/",
    "#class": xasiat.XasiatAlbumExtractor,
    "#count": 51,

    "title"         : "FRIDAYデジタル写真集 下村明香『Impact Beauty col.1』全カット",
    "album_category": "Gravure Idols",
    "model"         : ["Sayaka Shimomura"],
    "tags"          : [
        "FRIDAY Digital Photobook",
        "De Toute Beauté",
    ],
},

{
    "#url"     : "https://www.xasiat.com/albums/30478/gekkan-young-magazine-2025-no-11/",
    "#comment" : "no 'album_category' (#8569)",
    "#class"   : xasiat.XasiatAlbumExtractor,
    "#pattern" : r"https://www\.xasiat\.com/get_image/\d+/\w+",
    "#count"   : 13,

    "album_category": "",
    "album_id"      : 30478,
    "album_url"     : "https://www.xasiat.com/albums/30478/gekkan-young-magazine-2025-no-11/",
    "count"         : 13,
    "extension"     : "jpg",
    "model"         : [],
    "title"         : "[Gekkan Young Magazine] 2025 No.11",
    "tags"          : [
        "Young Magazine",
        "Teen",
    ],
},

{
    "#url"    : "https://www.xasiat.com/albums/categories/gravure-idols/",
    "#class"  : xasiat.XasiatCategoryExtractor,
    "#pattern": xasiat.XasiatAlbumExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://www.xasiat.com/albums/tags/japan/",
    "#class"  : xasiat.XasiatTagExtractor,
    "#pattern": xasiat.XasiatAlbumExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://www.xasiat.com/albums/models/remu-suzumori/",
    "#class"  : xasiat.XasiatModelExtractor,
    "#pattern": xasiat.XasiatAlbumExtractor.pattern,
    "#range"  : "1-15",
    "#count"  : 15,
},

)
