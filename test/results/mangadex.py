# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangadex
from gallery_dl import exception


__tests__ = (

{
    "#url"     : "https://mangadex.org/chapter/f946ac53-0b71-4b5d-aeb2-7931b13c4aaa",
    "#class"   : mangadex.MangadexChapterExtractor,
    "#count"   : 5,

    "artist"       : ["Oda Eiichiro"],
    "author"       : ["Oda Eiichiro"],
    "chapter"      : 6,
    "chapter_id"   : "f946ac53-0b71-4b5d-aeb2-7931b13c4aaa",
    "chapter_minor": "",
    "count"        : 5,
    "date"         : "dt:2018-02-28 10:42:50",
    "demographic"  : "shounen",
    "description"  : "One Piece Omake are short manga chapters originally published in the One Piece Log Books & Databooks.",
    "extension"    : {"jpg", "png"},
    "filename"     : str,
    "group"        : ["KEFI"],
    "lang"         : "en",
    "manga"        : "One Piece Omake",
    "manga_date"   : "dt:2018-06-29 17:22:51",
    "manga_id"     : "487f1f04-75f3-4a2e-a4af-76e615e32585",
    "origin"       : "ja",
    "page"         : range(1, 5),
    "rating"       : "safe",
    "status"       : "ongoing",
    "tags"         : ["Comedy"],
    "title"        : "The 6th Log - Chopper Man",
    "volume"       : 0,
    "year"         : None,
    "manga_titles" : [
        "One Piece: Log Book Omake",
        "One Piece: Mugiwara Theater",
        "One Piece: Straw Hat Theater",
        "One Piece: Strawhat Theater",
    ],
    "links"        : {
        "al" : "44414",
        "kt" : "24849",
        "mal": "14414",
    },
},

{
    "#url"     : "https://mangadex.org/chapter/61a88817-9c29-4281-bdf1-77b3c1be9831",
    "#comment" : "oneshot",
    "#class"   : mangadex.MangadexChapterExtractor,
    "#count"   : 64,

    "artist"       : ["Arakawa Hiromu"],
    "author"       : ["Arakawa Hiromu"],
    "chapter"      : 0,
    "chapter_id"   : "61a88817-9c29-4281-bdf1-77b3c1be9831",
    "chapter_minor": "",
    "count"        : 64,
    "date"         : "dt:2018-03-05 14:36:10",
    "demographic"  : "shounen",
    "description"  : "A kunoichi, Henpukumaru, awakens in the mansion of her enemy. She is introduced to the future lord of the mansion, Chiyozuru. Chiyozuru is able to get the unemotional Henpukumaru to smile and react differently than she normally would. But then Henpukumaru's former allies attack one night…",
    "extension"    : {"jpg", "png"},
    "filename"     : str,
    "group"        : ["Illuminati-Manga"],
    "lang"         : "en",
    "manga"        : "Souten no Koumori",
    "manga_date"   : "dt:2018-03-19 10:36:00",
    "manga_id"     : "f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
    "origin"       : "ja",
    "page"         : range(1, 64),
    "rating"       : "safe",
    "status"       : "completed",
    "title"        : "Oneshot",
    "volume"       : 0,
    "year"         : 2006,
    "manga_titles" : [
        "A Bat in Blue Sky",
        "Sôten no Kômori",
        "Soten no Komori",
        "蒼天の蝙蝠",
    ],
    "tags"         : [
        "Oneshot",
        "Historical",
        "Action",
        "Martial Arts",
        "Drama",
        "Tragedy",
    ],
    "links"        : {
        "al" : "30948",
        "ap" : "souten-no-koumori",
        "kt" : "2065",
        "mal": "948",
        "mu" : "opk9cgi",
    },
},

{
    "#url"     : "https://mangadex.org/chapter/74149a55-e7c4-44ea-8a37-98e879c1096f",
    "#comment" : "MANGA Plus (#1154)",
    "#class"   : mangadex.MangadexChapterExtractor,
    "#exception": exception.AbortExtraction,
},

{
    "#url"     : "https://mangadex.org/chapter/364728a4-6909-4164-9eea-6b56354f7c78",
    "#comment" : "'externalUrl', but *was* still downloadable, now 404 (#2503)",
    "#class"   : mangadex.MangadexChapterExtractor,
    "#exception": exception.AbortExtraction,
},

{
    "#url"     : "https://mangadex.org/chapter/f946ac53-0b71-4b5d-aeb2-7931b13c4aaa",
    "#class"   : mangadex.MangadexChapterExtractor,
    "#options" : {"data-saver": True},
    "#results" : (
        "https://cmdxd98sb0x3yprd.mangadex.network/data-saver/2780e594c3519e6858f76dfc018c8c1a/x1-d5962a0770b39faf73154b428be473752b4c379020916ecb5f0ffeac9639b6bf.jpg",
        "https://cmdxd98sb0x3yprd.mangadex.network/data-saver/2780e594c3519e6858f76dfc018c8c1a/x2-c9fcaf38888e38c48ff3cff0e2b342f68b7aaed2ea9e2a2a5446dc49b6a4d86e.jpg",
        "https://cmdxd98sb0x3yprd.mangadex.network/data-saver/2780e594c3519e6858f76dfc018c8c1a/x3-9ea5e06a4ba27b37dd66b75f1d267e3a6f8d21bb14a0163f669cf7f40ede315f.jpg",
        "https://cmdxd98sb0x3yprd.mangadex.network/data-saver/2780e594c3519e6858f76dfc018c8c1a/x4-605c869a362a19d016d7fb777908c9336fec995965cb59853cb7f9b3e128f70e.jpg",
        "https://cmdxd98sb0x3yprd.mangadex.network/data-saver/2780e594c3519e6858f76dfc018c8c1a/x5-dc40bd2b45d0ce26c7a401d74c2006a239f5839bc4f4a55893d035d6819627d7.jpg",
    ),
},

{
    "#url"     : "https://mangadex.org/title/f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
    "#comment" : "mutliple values for 'lang' (#4093)",
    "#class"   : mangadex.MangadexMangaExtractor,
    "#count"   : ">= 5",

    "manga"        : "Souten no Koumori",
    "manga_id"     : "f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
    "title"        : r"re:One[Ss]hot",
    "volume"       : 0,
    "chapter"      : 0,
    "chapter_minor": "",
    "chapter_id"   : str,
    "date"         : "type:datetime",
    "lang"         : "iso:lang",
    "artist"       : ["Arakawa Hiromu"],
    "author"       : ["Arakawa Hiromu"],
    "status"       : "completed",
    "tags"         : [
        "Oneshot",
        "Historical",
        "Action",
        "Martial Arts",
        "Drama",
        "Tragedy",
    ],
},

{
    "#url"     : "https://mangadex.org/title/f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
    "#comment" : "mutliple values for 'lang' (#4093)",
    "#class"   : mangadex.MangadexMangaExtractor,
    "#options" : {"lang": "fr,it"},
    "#count"   : 2,

    "manga"   : "Souten no Koumori",
    "lang"    : {"fr", "it"},
},

{
    "#url"     : "https://mangadex.cc/manga/d0c88e3b-ea64-4e07-9841-c1d2ac982f4a/",
    "#comment" : "removed",
    "#class"   : mangadex.MangadexMangaExtractor,
    "#options" : {"lang": "en"},
    "#count"   : 0,
},

{
    "#url"     : "https://mangadex.org/title/7c1e2742-a086-4fd3-a3be-701fd6cf0be9",
    "#class"   : mangadex.MangadexMangaExtractor,
    "#count"   : ">= 25",
},

{
    "#url"     : "https://mangadex.org/title/584ef094-b2ab-40ce-962c-bce341fb9d10",
    "#class"   : mangadex.MangadexMangaExtractor,
    "#count"   : ">= 20",
},

{
    "#url"     : "https://mangadex.org/title/2e73a1ac-bf26-4c04-84f6-d0a22fd37624/tomodachi-no-joshi-ni-josou-saserare-danshi",
    "#comment" : "no 'description' (#8389)",
    "#class"   : mangadex.MangadexMangaExtractor,
    "#count"   : 47,

    "description": "",
},

{
    "#url"     : "https://mangadex.org/titles/feed",
    "#class"   : mangadex.MangadexFeedExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://mangadex.org/title/feed",
    "#class"   : mangadex.MangadexFeedExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://mangadex.org/titles/follows",
    "#class"   : mangadex.MangadexFollowingExtractor,
    "#auth"    : True,
    "#results" : (
        "https://mangadex.org/title/cad76ec6-ca22-42f6-96f8-eca164da6545",
        "https://mangadex.org/title/7546ff2d-2310-47a4-b1f3-1a2561f20ce7",
    ),
},

{
    "#url"     : "https://mangadex.org/title/follows",
    "#class"   : mangadex.MangadexFollowingExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://mangadex.org/list/3a0982c5-65aa-4de2-8a4a-2175be7383ab/test",
    "#class"   : mangadex.MangadexListExtractor,
    "#results" : (
        "https://mangadex.org/title/cba4e5d6-67a0-47a0-b37a-c06e9bf25d93",
        "https://mangadex.org/title/cad76ec6-ca22-42f6-96f8-eca164da6545",
    ),
},

{
    "#url"     : "https://mangadex.org/list/3a0982c5-65aa-4de2-8a4a-2175be7383ab/test?tab=titles",
    "#class"   : mangadex.MangadexListExtractor,
},

{
    "#url"     : "https://mangadex.org/list/3a0982c5-65aa-4de2-8a4a-2175be7383ab/test?tab=feed",
    "#category": ("", "mangadex", "list-feed"),
    "#class"   : mangadex.MangadexListExtractor,
    "#results" : (
        "https://mangadex.org/chapter/c765d6d5-5712-4360-be0b-0c8e0914fc94",
        "https://mangadex.org/chapter/fa8a695d-260f-4dcc-95a3-1f30e66d6571",
        "https://mangadex.org/chapter/788766b9-41c6-422e-97ba-552f03ba9655",
    ),
},

{
    "#url"     : "https://mangadex.org/author/7222d0d5-836c-4bf3-9174-72bceade8c87/kotoyama",
    "#class"   : mangadex.MangadexAuthorExtractor,
    "#pattern" : mangadex.MangadexMangaExtractor.pattern,
    "#count"   : 9,
},

{
    "#url"     : "https://mangadex.org/author/254efca2-0ac0-432c-a3a3-55b7e207e87d/flipflops",
    "#class"   : mangadex.MangadexAuthorExtractor,
    "#pattern" : mangadex.MangadexMangaExtractor.pattern,
    "#options" : {"lang": "en"},
    "#count"   : ">= 15",
},

{
    "#url"     : "https://mangadex.org/title/f90c4398-8aad-4f51-8a1f-024ca09fdcbc?tab=art",
    "#class"   : mangadex.MangadexCoversExtractor,
    "#results" : "https://mangadex.org/covers/f90c4398-8aad-4f51-8a1f-024ca09fdcbc/af3c1690-1e06-4432-909e-3e0f9ee01f68.jpg",

    "artist"      : ["Arakawa Hiromu"],
    "author"      : ["Arakawa Hiromu"],
    "cover"       : "af3c1690-1e06-4432-909e-3e0f9ee01f68.jpg",
    "cover_id"    : "af3c1690-1e06-4432-909e-3e0f9ee01f68",
    "date"        : "dt:2021-05-24 17:19:13",
    "date_updated": "dt:2021-05-24 17:19:13",
    "extension"   : {"jpg", "png"},
    "filename"    : "af3c1690-1e06-4432-909e-3e0f9ee01f68",
    "lang"        : "ja",
    "manga"       : "Souten no Koumori",
    "manga_id"    : "f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
    "status"      : "completed",
    "volume"      : 0,
    "tags"        : [
        "Oneshot",
        "Historical",
        "Action",
        "Martial Arts",
        "Drama",
        "Tragedy",
    ],
},

{
    "#url"     : "https://mangadex.org/title/192aa767-2479-42c1-9780-8d65a2efd36a/gachiakuta?tab=art",
    "#class"   : mangadex.MangadexCoversExtractor,
    "#pattern" : r"https://mangadex\.org/covers/192aa767-2479-42c1-9780-8d65a2efd36a/[\w-]+\.jpg",
    "#count"   : 20,

    "artist"      : ["Urana Kei"],
    "author"      : ["Urana Kei"],
    "cover_id"    : "iso:uuid",
    "date"        : "type:datetime",
    "date_updated": "type:datetime",
    "extension"   : {"jpg", "png"},
    "filename"    : str,
    "lang"        : {"ja", "fa"},
    "manga"       : "GACHIAKUTA",
    "manga_id"    : "192aa767-2479-42c1-9780-8d65a2efd36a",
    "status"      : "ongoing",
    "volume"      : range(1, 20),
    "tags"        : [
        "Monsters",
        "Action",
        "Comedy",
        "Survival",
        "Drama",
        "Fantasy",
        "Delinquents",
        "Supernatural",
        "Tragedy",
    ],
},

)
