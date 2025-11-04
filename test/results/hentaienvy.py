# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imhentai


__tests__ = (
{
    "#url"     : "https://hentaienvy.com/gallery/12/",
    "#category": ("IMHentai", "hentaienvy", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://m1\.hentaienvy\.com/001/3x907ntq18/\d+\.jpg",
    "#count"   : 94,

    "count"     : 94,
    "extension" : "jpg",
    "filename"  : str,
    "gallery_id": 12,
    "lang"      : "en",
    "num"       : range(1, 94),
    "title"     : "(C67) [Studio Kimigabuchi (Kimimaru)] RE-TAKE 2 (Neon Genesis Evangelion) [English]",
    "title_alt" : "",
    "type"      : "doujinshi",
    "width"     : {835, 838, 841, 1200},
    "height"    : {862, 865, 1200},

    "artist":    [
        "kimimaru | entokkun",
    ],
    "character": [
        "asuka langley soryu",
        "gendo ikari",
        "makoto hyuga",
        "maya ibuki",
        "misato katsuragi",
        "rei ayanami",
        "shigeru aoba",
        "shinji ikari",
    ],
    "group": [
        "studio kimigabuchi",
    ],
    "language": [
        "english",
        "translated",
    ],
    "parody": [
        "neon genesis evangelion | shin seiki evangelion",
    ],
    "tags": [
        "multi-work series",
        "schoolboy uniform",
        "schoolgirl uniform",
        "sole female",
        "sole male",
        "story arc",
        "twintails",
    ],
},

{
    "#url"     : "https://hentaienvy.com/gallery/1293743/",
    "#category": ("IMHentai", "hentaienvy", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://m9\.hentaienvy\.com/029/tk70aw8b4y/\d+\.webp",
    "#count"   : 25,

    "count"     : 25,
    "num"       : range(1, 25),
    "extension" : "webp",
    "filename"  : str,
    "gallery_id": 1293743,
    "lang"      : "ru",
    "title"     : "(C102) [Koniro Kajitsu (KonKa)] Konbucha wa Ikaga desu ka | Хотите немного чая из водорослей? (Blue Archive) [Russian] [graun]",
    "title_alt" : "",
    "type"      : "doujinshi",
    "width"     : 1280,
    "height"    : range(1804, 1832),

    "artist": [
        "konka",
    ],
    "character": [
        "nagisa kirifuji",
        "sensei",
    ],
    "group": [
        "koniro kajitsu",
    ],
    "language": [
        "russian",
        "translated",
    ],
    "parody": [
        "blue archive",
    ],
    "tags": [
        "angel",
        "defloration",
        "halo",
        "kissing",
        "pantyhose",
        "sole female",
        "sole male",
        "wings",
    ],
},

{
    "#url"     : "https://hentaienvy.com/artist/asutora/",
    "#category": ("IMHentai", "hentaienvy", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(45, 50),
},

{
    "#url"     : "https://hentaienvy.com/search/?s_key=asutora",
    "#category": ("IMHentai", "hentaienvy", "search"),
    "#class"   : imhentai.ImhentaiSearchExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(45, 60),
},

{
    "#url"     : "https://hentaienvy.com/advanced-search/?key=%2Btag%3A%22Monster+Girl%22+%2Bcharacter%3A%22Gardevoir%22&lt=1&m=1&d=1&w=1&i=1&a=1&g=1&en=1",
    "#comment" : "'/advanced-search/' URL (#8507)",
    "#category": ("IMHentai", "hentaienvy", "search"),
    "#class"   : imhentai.ImhentaiSearchExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(185, 200),
},

)
