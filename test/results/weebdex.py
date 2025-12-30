# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import weebdex


__tests__ = (
{
    "#url"     : "https://weebdex.org/chapter/f6c0awnrba",
    "#class"   : weebdex.WeebdexChapterExtractor,
    "#pattern" : r"https://s\d+\.notdelta\.xyz/data/f6c0awnrba/\d+-\w{64}\.png",
    "#count"   : 14,

    "artist"       : ["Nokomi (のこみ)"],
    "author"       : ["Tanabata Satori"],
    "chapter"      : 11,
    "chapter_id"   : "f6c0awnrba",
    "chapter_minor": ".5",
    "count"        : 14,
    "page"         : range(1, 14),
    "date"         : "dt:2025-10-13 10:47:26",
    "date_updated" : "type:datetime",
    "demographic"  : "shoujo",
    "extension"    : "png",
    "filename"     : str,
    "group"        : ["Knights of Earl Grey"],
    "width"        : range(800, 2800),
    "height"       : range(800, 2800),
    "lang"         : "en",
    "manga"        : "Akuyaku Reijou Level 99 ~Watashi wa UraBoss desu ga Maou de wa Arimasen~",
    "manga_date"   : "dt:2025-10-09 07:32:07",
    "manga_id"     : "raa6dfy3da",
    "origin"       : "ja",
    "status"       : "ongoing",
    "title"        : "[Extra] A Day In The Life Of Patrick",
    "uploader"     : "system",
    "version"      : 1,
    "volume"       : 2,
    "year"         : 2020,
    "description"  : """\
I reincarnated as the "Villainess Eumiella" from an RPG Otome game. In the main story, Eumiella is merely a side character, but after the ending, she re-enters the story as the Hidden Boss, a character boasting high stats on par with the heroes! Lighting a fire in my gamer's soul, and taking advantage of being left on my own in my parent's territory, I trained, trained, and trained! As a result of my training... by the time I enrolled in the academy, I managed to reach level 99. Though I had planned to live out my days as inconspicuously and peacefully as possible, soon after entering the school, I'm suspected by the Heroine and Love Interests of being the "Demon Lord"...?
___
**Links:**
- Alternative Official Raw - [Niconico](https://manga.nicovideo.jp/comic/46067)\
""",
    "tags"         : [
        "format:Adaptation",
        "genre:Action",
        "genre:Comedy",
        "genre:Fantasy",
        "genre:Isekai",
        "genre:Romance",
        "theme:Demons",
        "theme:Magic",
        "theme:Monsters",
        "theme:Reincarnation",
        "theme:School Life",
        "theme:Video Games",
        "theme:Villainess",
    ],
},

{
    "#url"     : "https://weebdex.org/chapter/itizot1rxc",
    "#class"   : weebdex.WeebdexChapterExtractor,
    "#pattern" : r"https://s\d+\.notdelta\.xyz/data/itizot1rxc/\d+\-\w+\.jpg",
    "#count"   : 17,

    "artist"       : ["Matsuda Minoru"],
    "author"       : ["Matsuda Minoru"],
    "chapter"      : 10,
    "chapter_id"   : "itizot1rxc",
    "chapter_minor": "",
    "count"        : 17,
    "demographic"  : "seinen",
    "group"        : ["BBB Translation (Big Beaming Bluewhale)"],
    "lang"         : "vi",
    "manga"        : "Ani Datta Mono",
    "manga_date"   : "dt:2025-10-09 19:02:04",
    "manga_id"     : "3o0icxno26",
    "origin"       : "ja",
    "title"        : "Cuộc hẹn tại phía Đông vườn địa đàng",
    "uploader"     : "sMrBjZf",
    "version"      : 1,
    "volume"       : 2,
    "year"         : 2021,
},

{
    "#url"     : "https://weebdex.org/title/3o0icxno26/ani-datta-mono",
    "#class"   : weebdex.WeebdexMangaExtractor,
    "#pattern" : weebdex.WeebdexChapterExtractor.pattern,
    "#count"   : range(120, 300),

    "artist"       : ["Matsuda Minoru"],
    "author"       : ["Matsuda Minoru"],
    "volume"       : int,
    "chapter"      : int,
    "chapter_minor": {"", ".5"},
    "created_at"   : "iso:dt",
    "published_at" : "iso:dt",
    "updated_at"   : "iso:dt",
    "demographic"  : "seinen",
    "id"           : str,
    "language"     : {"en", "vi"},
    "manga"        : "Ani Datta Mono",
    "manga_date"   : "dt:2025-10-09 19:02:04",
    "manga_id"     : "3o0icxno26",
    "origin"       : "ja",
    "status"       : "ongoing",
    "version"      : {1, 2},
    "year"         : 2021,
    "description"  : """\
My brother died. When I went to visit my brother's grave with my brother's lover——……

This is the story of my brother's lover, me, and “the thing that was my brother”.
___
**Additional Links:**
- [Official TikTok](http://tiktok.com/@anidattamono)
- [Official X](https://x.com/anidattamono)\
""",
    "tags"         : [
        "genre:Drama",
        "genre:Horror",
        "genre:Psychological",
        "genre:Romance",
        "genre:Thriller",
        "theme:Ghosts",
        "theme:Supernatural",
    ],
},

)
