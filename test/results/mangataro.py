# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangataro


__tests__ = (
{
    "#url"     : "https://mangataro.org/read/majo-to-youhei/ch8-356833",
    "#class"   : mangataro.MangataroChapterExtractor,
    "#pattern" : r"https://bx1\.mangapeak\.me/storage/chapters/b99b2860f0444d924c9446b4ecf1cdad/\d+\.webp",
    "#count"   : 22,

    "chapter"      : 8,
    "chapter_minor": "",
    "chapter_id"   : 356833,
    "chapter_url"  : "https://mangataro.org/read/majo-to-youhei/ch8-356833",
    "count"        : 22,
    "page"         : range(1, 22),
    "cover"        : "https://mangataro.org/content/media/301979l.jpg",
    "date"         : "dt:2025-05-03 19:04:48",
    "date_updated" : "dt:2025-05-03 19:04:53",
    "description"  : "<p>Zig—a tall, broad-shouldered mercenary—participates in a witch hunt. Following a fierce duel with the deadly witch, he becomes privy to her desire. “I want you to protect me,” she requests, tired of having her life trivialized. Seeking a place to survive, the witch and the mercenary set their sights on an unknown continent!</p><p>(Source: Kodansha USA)</p></div><div class=\"mt-6 pt-6 border-t border-neutral-700/30\"><div class=\"flex items-center gap-2 mb-3\"> <svg class=\"w-4 h-4 text-neutral-400\" fill=\"none\" viewBox=\"0 0 24 24\" stroke=\"currentColor\"> <path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z\" /> </svg><h4 class=\"text-sm font-medium text-neutral-100\">Background</h4></div><div class=\"max-w-none text-neutral-400 text-justify text-xs\"><p>Majo to Youhei has been published digitally as an English simulpub as The Witch and the Mercenary by Kodansha USA through K Manga.</p>",
    "filename"     : str,
    "extension"    : "webp",
    "genre"        : "Manga",
    "manga"        : "Majo to Youhei",
    "manga_url"    : "https://mangataro.org/manga/majo-to-youhei",
    "publisher"    : "Magazine pocket",
    "status"       : "Ongoing",
    "title"        : "It’s Just a Knife",
    "author"       : [
        "Miyagi",
        "Makoto",
        "Chouhoukiteki",
        "Kaeru",
    ],
    "tags"         : [
        "Action",
        "Fantasy",
    ],
},

{
    "#url"     : "https://mangataro.org/read/sono-akuyaku-kizoku-mama-heroine-ga-sukisugiru-shinshi-na-doryoku-de-saikyou-to-nari-fuguu-na-oshi-chara-tasukemakuru/ch12-2-337633",
    "#class"   : mangataro.MangataroChapterExtractor,
    "#pattern" : r"https://bx1\.mangapeak\.me/storage/chapters/200aa5d11c6ef1f049a2c68163c3a1d7/\d+\.webp",
    "#count"   : 13,

    "chapter"      : 12,
    "chapter_minor": ".2",
    "chapter_id"   : 337633,
    "chapter_url"  : "https://mangataro.org/read/sono-akuyaku-kizoku-mama-heroine-ga-sukisugiru-shinshi-na-doryoku-de-saikyou-to-nari-fuguu-na-oshi-chara-tasukemakuru/ch12-2-337633",
    "count"        : 13,
    "page"         : range(1, 13),
    "cover"        : "https://mangataro.org/content/media/317553l.webp",
    "date"         : "dt:2025-04-25 14:25:53",
    "date_updated" : "dt:2025-04-25 14:25:57",
    "description"  : "<p>The mom characters that appear in the game are all unfortunate sub-heroines who always get bad ending routes. “Why… Why does such a cute mom have to die?!” Even though the protagonist tried very hard to request a route where they get saved, all of his efforts were in vain, making him spend his days in frustration. Then, he suddenly gets reincarnated into the world of MamaFan on a certain day. …However, he gets reincarnated as a villainous aristocrat who’s got nothing but the worst routes. This guy, who’s crazy about mom characters—his fulfilling days of saving his beloved mom characters and his journey to create his harem full of plump women are about to begin!</p><p>(Source: Kadokawa, translated)</p>",
    "filename"     : str,
    "extension"    : "webp",
    "genre"        : "Manga",
    "manga"        : "The Villainous Noble Loves Mom Heroines Too Much: Becoming The Strongest With Sincere Effort To Save Misfortunate Fave Chars",
    "manga_url"    : "https://mangataro.org/manga/sono-akuyaku-kizoku-mama-heroine-ga-sukisugiru-shinshi-na-doryoku-de-saikyou-to-nari-fuguu-na-oshi-chara-tasukemakuru",
    "publisher"    : "Web Comic Apanta",
    "status"       : "Ongoing",
    "title"        : "",
    "author"       : [
        "Nozomi",
        "Kota",
        "Oomine",
    ],
    "tags"         : [
        "Fantasy",
        "Ecchi",
    ],
},

{
    "#url"     : "https://mangataro.org/manga/hinmin-choujin-kanenashi-kun",
    "#class"   : mangataro.MangataroMangaExtractor,
    "#pattern" : mangataro.MangataroChapterExtractor.pattern,
    "#count"   : 47,

    "author"       : ["Pageratta"],
    "chapter"      : int,
    "chapter_id"   : int,
    "chapter_minor": {"", ".5", ".9"},
    "cover"        : "https://mangataro.org/content/media/199106l.webp",
    "description"  : "<p>The everyday life of a poor student, Kamenashi, as documented by his classmate who has a crush on him!</p>",
    "genre"        : "Manga",
    "manga"        : "Hinmin Choujin Kanenashi-kun",
    "manga_url"    : "https://mangataro.org/manga/hinmin-choujin-kanenashi-kun",
    "publisher"    : "Shounen Jump+",
    "status"       : "Completed",
    "tags"         : [
        "Comedy",
        "Romance",
    ],
},

{
    "#url"     : "https://mangataro.org/manga/lookism",
    "#class"   : mangataro.MangataroMangaExtractor,
    "#pattern" : mangataro.MangataroChapterExtractor.pattern,
    "#count"   : 573,

    "chapter"      : range(1, 573),
    "chapter_id"   : int,
    "chapter_minor": "",
    "cover"        : "https://mangataro.org/content/media/208866l.webp",
    "description"  : "<p>Park Hyung Suk has spent all 17 years of his life at the bottom of the food chain. Short, overweight, and unattractive, he is used to being bullied by his classmates and constantly discriminated against for his looks. In an attempt to escape his biggest bully, Lee Tae Sung, he decides to transfer to Seoul’s Jae Won High School, a vocational preparatory school notorious for its liberal education system and carefree students. Days before his transfer, Hyung Suk wakes to find that he is no longer in his usual chubby body, but is instead in a perfect body! Tall, handsome, and beautifully toned, Hyung Suk has become the ideal version of himself. The only problem is that his original body still lays beside him—and when one body falls asleep, he awakens in the other. Now possessing two extremely different bodies, Hyung Suk must learn to navigate his new and much more popular life at J High whilst also solving the mystery of where his second, almost superhuman, body came from. [Written by MAL Rewrite]</p></div><div class=\"mt-6 pt-6 border-t border-neutral-700/30\"><div class=\"flex items-center gap-2 mb-3\"> <svg class=\"w-4 h-4 text-neutral-400\" fill=\"none\" viewBox=\"0 0 24 24\" stroke=\"currentColor\"> <path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z\" /> </svg><h4 class=\"text-sm font-medium text-neutral-100\">Background</h4></div><div class=\"max-w-none text-neutral-400 text-justify text-xs\"><p>Lookism is originally a webtoon which first volume was officially published in paperbook format by &Book (대원앤북) on May 25, 2017. The series has been serialized in English by LINE Webtoon since June 4, 2017.</p>",
    "genre"        : "Manhwa",
    "manga"        : "Lookism",
    "manga_url"    : "https://mangataro.org/manga/lookism",
    "publisher"    : "Naver Webtoon",
    "status"       : "Ongoing",
    "author"       : [
        "Park",
        "Tae-Jun",
    ],
    "tags"         : [
        "Action",
        "Comedy",
        "Drama",
        "Supernatural",
    ],
},

)
