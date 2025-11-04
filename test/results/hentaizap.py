# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imhentai


__tests__ = (
{
    "#url"     : "https://hentaizap.com/gallery/12/",
    "#category": ("IMHentai", "hentaizap", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://m1\.hentaizap\.com/001/3x907ntq18/\d+\.jpg",
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
    "#url"     : "https://hentaizap.com/gallery/1329498/",
    "#category": ("IMHentai", "hentaizap", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://m9\.hentaizap\.com/029/tk70aw8b4y/\d+\.webp",
    "#count"   : 25,

    "count"     : 25,
    "num"       : range(1, 25),
    "extension" : "webp",
    "filename"  : str,
    "gallery_id": 1329498,
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
    "#url"     : "https://hentaizap.com/artist/asutora/",
    "#category": ("IMHentai", "hentaizap", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(45, 50),
},

{
    "#url"     : "https://hentaizap.com/search/?key=asutora",
    "#category": ("IMHentai", "hentaizap", "search"),
    "#class"   : imhentai.ImhentaiSearchExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(45, 60),
},

)
