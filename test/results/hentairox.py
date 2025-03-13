# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imhentai


__tests__ = (
{
    "#url"     : "https://hentairox.com/gallery/25/",
    "#category": ("IMHentai", "hentairox", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://m1\.hentairox\.com/001/knrxtga49v/\d+\.jpg",
    "#count"   : 25,

    "count"     : 25,
    "extension" : "jpg",
    "filename"  :  r"re:\d+",
    "gallery_id": 25,
    "lang"      : "ja",
    "num"       : range(1, 25),
    "title"     : "(Shikei wa Iyadakara na) [Kujira Logic, TOYBOX (Kujiran, Kurikara)] Gensou-kyou Chichi Zukan - Kurenai (Touhou Project)",
    "title_alt" : "(死刑はいやだからな) [くぢらろじっく, といぼっくす (くぢらん, くりから)] 幻想郷乳図鑑 - 紅 (東方Project)",
    "type"      : "doujinshi",
    "width"     : {696, 701},
    "height"    : {999, 1000},

    "artist": [
        "kujiran",
        "kurikara",
    ],
    "character": [
        "hong meiling",
        "koakuma",
        "patchouli knowledge",
        "remilia scarlet",
        "sakuya izayoi",
    ],
    "group": [
        "kujira logic",
        "toybox",
    ],
    "language": [
        "japanese",
    ],
    "parody": [
        "touhou project",
    ],
    "tags": [
        "big breasts",
        "footjob",
        "futanari",
        "lolicon",
        "maid",
        "paizuri",
    ],
},

{
    "#url"    : "https://hentairox.com/gallery/8526/",
    "#category": ("IMHentai", "hentairox", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern": r"https://m1\.hentairox\.com/001/gkchsf3x5m/\d+\.jpg",
    "#count"  : 8,

    "count"     : 8,
    "extension" : "jpg",
    "filename"  : r"re:\d+",
    "gallery_id": 8526,
    "lang"      : "ja",
    "num"       : range(1, 8),
    "title"     : "(C70) [UDON-YA (Kizuki Aruchu, ZAN)] Udonko CM70 Omake Hon (Various)",
    "title_alt" : "(C70) [うどんや (鬼月あるちゅ、ZAN)] うどんこ CM70オマケ本 (よろず)",
    "type"      : "doujinshi",
    "width"     : 1076,
    "height"    : 1517,

    "artist": [
        "kizuki aruchu",
        "zan",
    ],
    "character": [
        "mikuru asahina",
        "reisen udongein inaba",
        "tsuruya",
    ],
    "group": [
        "udon-ya",
    ],
    "language": [
        "japanese",
    ],
    "parody": [
        "fate stay night",
        "super robot wars | super robot taisen",
        "the melancholy of haruhi suzumiya | suzumiya haruhi no yuuutsu",
    ],
    "tags": [
        "big breasts",
        "okaasan to issho",
        "touhou kaeidzuka",
    ],
},

{
    "#url"     : "https://hentairox.com/artist/kizuki-aruchu/",
    "#category": ("IMHentai", "hentairox", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(140, 160),
},

{
    "#url"     : "https://hentairox.com/search/?key=aruchu",
    "#category": ("IMHentai", "hentairox", "search"),
    "#class"   : imhentai.ImhentaiSearchExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(140, 160),
},

)
