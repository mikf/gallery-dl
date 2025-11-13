# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imhentai


__tests__ = (
{
    "#url"     : "https://imhentai.xxx/gallery/12/",
    "#category": ("IMHentai", "imhentai", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://m1\.imhentai\.xxx/001/3x907ntq18/\d+\.jpg",
    "#count"   : 94,

    "count"     : 94,
    "extension" : "jpg",
    "filename"  : str,
    "gallery_id": 12,
    "lang"      : "en",
    "num"       : range(1, 94),
    "title"     : "(C67) [Studio Kimigabuchi (Kimimaru)] RE-TAKE 2 (Neon Genesis Evangelion) [English]",
    "title_alt" : "(C67) [スタジオKIMIGABUCHI (きみまる)] RE-TAKE2 (新世紀エヴァンゲリオン) [英訳]",
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
    "#url"     : "https://imhentai.xxx/gallery/1396508/",
    "#category": ("IMHentai", "imhentai", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://m9\.imhentai\.xxx/028/po9f4w3jzx/\d+\.webp",
    "#count"   : 34,

    "count"     : 34,
    "extension" : "webp",
    "filename"  : str,
    "gallery_id": 1396508,
    "lang"      : "ko",
    "num"       : range(1, 34),
    "title"     : "[Beruennea (Skylader)] Tada no Kouhai ni Natta Kimi | 그냥 후배가 돼 버린 너 [Korean] [Digital]",
    "title_alt" : "[ベルエンネーア (すかいれーだー)] ただの後輩になった君 [韓国翻訳] [DL版]",
    "type"      : "doujinshi",
    "width"     : 1280,
    "height"    : {1790, 1791},

    "artist": [
        "skylader",
    ],
    "character": [],
    "group": [
        "beruennea",
    ],
    "language": [
        "korean",
        "translated",
    ],
    "parody": [
        "original",
    ],
    "tags": [
        "ahegao",
        "big ass",
        "big breasts",
        "big nipples",
        "big penis",
        "bike shorts",
        "blowjob",
        "gokkun",
        "hairy",
        "huge breasts",
        "mosaic censorship",
        "muscle",
        "nakadashi",
        "netorare",
        "schoolgirl uniform",
        "tanlines",
    ],
},

{
    "#url"     : "https://imhentai.xxx/artist/asutora/",
    "#category": ("IMHentai", "imhentai", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(45, 50),
},

{
    "#url"     : "https://imhentai.xxx/search/?lt=1&pp=0&m=1&d=1&w=1&i=1&a=1&g=1&key=asutora&apply=Search&en=1&jp=1&es=1&fr=1&kr=1&de=1&ru=1&dl=0&tr=0",
    "#category": ("IMHentai", "imhentai", "search"),
    "#class"   : imhentai.ImhentaiSearchExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(45, 60),
},

)
