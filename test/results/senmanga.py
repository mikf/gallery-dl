# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import senmanga


__tests__ = (
{
    "#url"     : "https://raw.senmanga.com/Bokura-wa-Minna-Kawaisou/37A/1",
    "#category": ("", "senmanga", "chapter"),
    "#class"   : senmanga.SenmangaChapterExtractor,
    "#pattern"     : r"https://raw\.senmanga\.com/viewer/Bokura-wa-Minna-Kawaisou/37A/[12]",
    "#sha1_url"    : "5f95140ff511d8497e2ec08fa7267c6bb231faec",
    "#sha1_content": "556a16d5ca3441d7a5807b6b5ac06ec458a3e4ba",

    "chapter"  : "37A",
    "count"    : 2,
    "extension": "",
    "filename" : r"re:[12]",
    "lang"     : "ja",
    "language" : "Japanese",
    "manga"    : "Bokura wa Minna Kawaisou",
    "page"     : int,
},

{
    "#url"     : "http://raw.senmanga.com/Love-Lab/2016-03/1",
    "#category": ("", "senmanga", "chapter"),
    "#class"   : senmanga.SenmangaChapterExtractor,
    "#pattern" : r"https://raw\.senmanga\.com/viewer/Love-Lab/2016-03/\d",
    "#sha1_url": "8347b9f00c14b864dd3c19a1f5ae52adb2ef00de",

    "chapter"  : "2016-03",
    "count"    : 9,
    "extension": "",
    "filename" : r"re:\d",
    "manga"    : "Renai Lab   恋愛ラボ",
},

{
    "#url"     : "https://raw.senmanga.com/akabane-honeko-no-bodyguard/1",
    "#category": ("", "senmanga", "chapter"),
    "#class"   : senmanga.SenmangaChapterExtractor,
    "#pattern" : r"https://i\d\.wp\.com/kumacdn.club/image-new-2/a/akabane-honeko-no-bodyguard/chapter-1/\d+-[0-9a-f]{13}\.jpg",

    "chapter"  : "1",
    "count"    : 65,
    "extension": "jpg",
    "filename" : r"re:\d+-\w+",
    "manga"    : "Akabane Honeko no Bodyguard",
},

{
    "#url"     : "https://raw.senmanga.com/amama-cinderella/3",
    "#comment" : "no http scheme ()",
    "#category": ("", "senmanga", "chapter"),
    "#class"   : senmanga.SenmangaChapterExtractor,
    "#pattern" : r"^https://kumacdn.club/image-new-2/a/amama-cinderella/chapter-3/.+\.jpg",
    "#count"   : 30,
},

)
