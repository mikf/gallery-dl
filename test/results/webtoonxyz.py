# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import webtoonxyz


__tests__ = (
{
    "#url"     : "https://www.webtoon.xyz/",
    "#category": ("wpmadara", "webtoonxyz", "home"),
    "#class"   : webtoonxyz.WebtoonxyzHomeExtractor,
    "#pattern" : webtoonxyz.WebtoonxyzMangaExtractor.pattern,
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : (
        "https://www.webtoon.xyz/read/"
        "i-became-an-apartment-security-manager/chapter-1/"
    ),
    "#category": ("wpmadara", "webtoonxyz", "chapter"),
    "#class"   : webtoonxyz.WebtoonxyzChapterExtractor,
    "#pattern" : (
        r"https://cdn8\.webtoon\.xyz/manga_68989afff3159/"
        r"bba27c1e700f002c9476a982e8883101/\d{2}\.jpg"
    ),
    "#count"   : 15,

    "artist"       : ["Beluga"],
    "author"       : ["Bibik"],
    "chapter"      : 1,
    "chapter_minor": "",
    "count"        : 15,
    "description"  : r"re:Lee Han's life was going nowhere until he "
                     r"received an offer too tempting and dangerous to "
                     r"ignore\.",
    "extension"    : "jpg",
    "genres"       : [
        "Drama",
        "Harem",
        "Mature",
    ],
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "I Became an Apartment Security Manager",
    "manga_alt"    : ["아파트 관리인이 되었다"],
    "rating"       : 4.3,
    "release"      : 2025,
    "status"       : "OnGoing",
    "title"        : "",
    "type"         : "Manhwa",
},

{
    "#url"     : "https://www.webtoon.xyz/read/the-monster-in-my-room/"
                 "chapter-42-01/",
    "#category": ("wpmadara", "webtoonxyz", "chapter"),
    "#class"   : webtoonxyz.WebtoonxyzChapterExtractor,
},

{
    "#url"     : (
        "https://www.webtoon.xyz/read/"
        "i-became-an-apartment-security-manager/"
    ),
    "#category": ("wpmadara", "webtoonxyz", "manga"),
    "#class"   : webtoonxyz.WebtoonxyzMangaExtractor,
    "#pattern" : webtoonxyz.WebtoonxyzChapterExtractor.pattern,
    "#count"   : 34,

    "artist"       : ["Beluga"],
    "author"       : ["Bibik"],
    "chapter"      : range(1, 35),
    "chapter_minor": "",
    "description"  : r"re:Lee Han's life was going nowhere until he "
                     r"received an offer too tempting and dangerous to "
                     r"ignore\.",
    "genres"       : [
        "Drama",
        "Harem",
        "Mature",
    ],
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "I Became an Apartment Security Manager",
    "manga_alt"    : ["아파트 관리인이 되었다"],
    "rating"       : 4.3,
    "release"      : 2025,
    "status"       : "OnGoing",
    "title"        : "",
    "type"         : "Manhwa",
},

{
    "#url"     : "https://www.webtoon.xyz/read/"
                 "i-became-an-apartment-security-manager",
    "#category": ("wpmadara", "webtoonxyz", "manga"),
    "#class"   : webtoonxyz.WebtoonxyzMangaExtractor,
},

)
