# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xasiat


__tests__ = (
{
    "#url"  : "https://www.xasiat.com/albums/28156/photobook-2024-12-09-bomb/",
    "#class": xasiat.XasiatAlbumExtractor,
    "#count": 61,

    "title"         : "[Photobook] 2024.12.09 白濱美兎『忘れられない恋の味』BOMBデジタル写真集",
    "album_category": "JAV & AV Models",
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
    "tags"          : [
        "コスプレ",
    ],
},

{
    "#url"  : "https://www.xasiat.com/fr/albums/23354/friday-impact-beauty-col-1/",
    "#class": xasiat.XasiatAlbumExtractor,
    "#count": 51,

    "title"         : "FRIDAYデジタル写真集 下村明香『Impact Beauty col.1』全カット",
    "album_category": "Gravure Idols",
    "tags"         : [
        "FRIDAY Digital Photobook",
        "De Toute Beauté",
    ],
    "model"        : [
        "Sayaka Shimomura",
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
