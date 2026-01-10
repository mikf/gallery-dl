# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import ahottie


__tests__ = (
{
    "#url"     : "https://ahottie.top/albums/5d54b221c19ff9c9126ffd62859c6603",
    "#comment" : "multiple pages (#8862)",
    "#class"   : ahottie.AhottieGalleryExtractor,
    "#pattern" : r"https://images2\.imgbox\.com/../../\w+_o\.jpg",
    "#count"   : 14,

    "count"     : 14,
    "num"       : range(1, 14),
    "date"      : "dt:2024-12-30 00:00:00",
    "extension" : "jpg",
    "filename"  : str,
    "gallery_id": "5d54b221c19ff9c9126ffd62859c6603",
    "title"     : "大熊杏優・かれしちゃん, Young Champion 2025 No.02 (ヤングチャンピオン 2025年2号)",
    "tags"      : [
        "Ayu Okuma 大熊杏優",
        "Kareshichan かれしちゃん",
        "Young Champion ヤングチャンピオン",
    ],
},

{
    "#url"     : "https://ahottie.top/tags/Ayu%20Okuma%20%E5%A4%A7%E7%86%8A%E6%9D%8F%E5%84%AA",
    "#class"   : ahottie.AhottieTagExtractor,
    "#pattern" : ahottie.AhottieGalleryExtractor.pattern,
    "#count"   : 17,

    "date"       : "type:datetime",
    "search_tags": "Ayu Okuma 大熊杏優",
    "title"      : str,
    "url"        : str,
},

{
    "#url"     : "https://ahottie.top/search?kw=ayu&page=10",
    "#class"   : ahottie.AhottieSearchExtractor,
    "#pattern" : ahottie.AhottieGalleryExtractor.pattern,
    "#count"   : range(80, 200),

    "date"       : "type:datetime",
    "search_tags": "ayu",
    "title"      : str,
    "url"        : str,
},

)
