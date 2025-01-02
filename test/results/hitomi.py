# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hitomi


__tests__ = (
{
    "#url"     : "https://hitomi.la/galleries/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#pattern"      : r"https://[a-c]a\.hitomi\.la/webp/\d+/\d+/[0-9a-f]{64}\.webp",
    "#count"        : 16,

    "artist"    : ["morris"],
    "characters": [],
    "count"     : 16,
    "date"      : "dt:2015-10-27 19:20:00",
    "extension" : "webp",
    "extension_original" : "jpg",
    "filename"  : str,
    "gallery_id": 867789,
    "group"     : [],
    "lang"      : "en",
    "language"  : "English",
    "num"       : range(1, 16),
    "parody"    : [],
    "tags"      : [
        "Cheating ♀",
        "Drugs ♀",
        "Drugs ♂",
        "Incest",
        "Milf ♀",
        "Mother ♀",
        "Sole Female ♀",
        "Sole Male ♂",
        "Uncensored"
    ],
    "title"     : "Amazon no Hiyaku | Amazon Elixir (decensored)",
    "title_jpn" : "",
    "type"      : "Manga",
},

{
    "#url"     : "https://hitomi.la/galleries/1401410.html",
    "#comment" : "download test",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#range"       : "1",
    "#sha1_content": "d75d5a3d1302a48469016b20e53c26b714d17745",
},

{
    "#url"     : "https://hitomi.la/galleries/733697.html",
    "#comment" : "Game CG with scenes (#321)",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#count"   : 210,
},

{
    "#url"     : "https://hitomi.la/galleries/1045954.html",
    "#comment" : "fallback for galleries only available through /reader/ URLs",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#count"   : 1413,
},

{
    "#url"     : "https://hitomi.la/cg/scathacha-sama-okuchi-ecchi-1291900.html",
    "#comment" : "gallery with 'broken' redirect",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/cg/1615823.html",
    "#comment" : "no tags",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#options" : {"format": "avif"},
    "#pattern" : r"https://[a-c]a\.hitomi\.la/avif/\d+/\d+/[0-9a-f]{64}\.avif",
    "#count"   : 22,

    "artist"    : ["sorairo len"],
    "characters": [],
    "count"     : 22,
    "date"      : "dt:2020-04-19 06:33:00",
    "extension" : "avif",
    "filename"  : str,
    "gallery_id": 1615823,
    "group"     : [],
    "lang"      : "ja",
    "language"  : "Japanese",
    "num"       : range(1, 22),
    "parody"    : [],
    "tags"      : [
        "Blowjob ♀",
        "Focus Blowjob ♀",
        "Fox Girl ♀",
        "Kemonomimi ♀",
        "Loli ♀",
        "Miko ♀",
        "No Penetration",
        "Unusual Pupils ♀",
        "Variant Set"
    ],
    "title"     : "Kouko-sama ga Okuchi de Reiryoku Hokyuu",
    "title_jpn" : "コウコ様がお口で霊力補給♡",
    "type"      : "Artistcg",
},

{
    "#url"     : "https://hitomi.la/manga/amazon-no-hiyaku-867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/manga/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/doujinshi/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/cg/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/gamecg/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/imageset/867789.html",
    "#comment" : "/imageset/ gallery (#4756)",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/reader/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/tag/screenshots-japanese.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
    "#pattern" : hitomi.HitomiGalleryExtractor.pattern,
    "#count"   : ">= 35",

    "search_tags": "screenshots",
},

{
    "#url"     : "https://hitomi.la/artist/a1-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/group/initial%2Dg-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/series/amnesia-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/type/doujinshi-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/character/a2-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/index-japanese.html",
    "#class"   : hitomi.HitomiIndexExtractor,
    "#pattern" : hitomi.HitomiGalleryExtractor.pattern,
    "#range"   : "1-150",
    "#count"   : 150,
},

{
    "#url"     : "https://hitomi.la/search.html?tag%3Ascreenshots%20language%3Ajapanese",
    "#class"   : hitomi.HitomiSearchExtractor,
    "#pattern" : hitomi.HitomiGalleryExtractor.pattern,
    "#range"   : "1-150",
    "#count"   : 150,

    "search_tags": "tag:screenshots language:japanese",
},

{
    "#url"     : "https://hitomi.la/search.html?female%3Asole_female%20language%3Ajapanese%20artist%3Asumiya",
    "#class"   : hitomi.HitomiSearchExtractor,
    "#pattern" : hitomi.HitomiGalleryExtractor.pattern,
    "#count"   : range(35, 50),

    "search_tags": "female:sole_female language:japanese artist:sumiya",
},

{
    "#url"     : "https://hitomi.la/search.html?group:initial_g",
    "#class"   : hitomi.HitomiSearchExtractor,
},
{
    "#url"     : "https://hitomi.la/search.html?series:amnesia",
    "#class"   : hitomi.HitomiSearchExtractor,
},
{
    "#url"     : "https://hitomi.la/search.html?type%3Adoujinshi",
    "#class"   : hitomi.HitomiSearchExtractor,
},
{
    "#url"     : "https://hitomi.la/search.html?character%3Aa2",
    "#class"   : hitomi.HitomiSearchExtractor,
},

)
