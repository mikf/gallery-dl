# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangadex
from gallery_dl import exception
import datetime


__tests__ = (
{
    "#url"     : "https://mangadex.org/chapter/f946ac53-0b71-4b5d-aeb2-7931b13c4aaa",
    "#category": ("", "mangadex", "chapter"),
    "#class"   : mangadex.MangadexChapterExtractor,
    "#sha1_metadata": "e86128a79ebe7201b648f1caa828496a2878dc8f",
},

{
    "#url"     : "https://mangadex.org/chapter/61a88817-9c29-4281-bdf1-77b3c1be9831",
    "#comment" : "oneshot",
    "#category": ("", "mangadex", "chapter"),
    "#class"   : mangadex.MangadexChapterExtractor,
    "#count"        : 64,
    "#sha1_metadata": "d11ed057a919854696853362be35fc0ba7dded4c",
},

{
    "#url"     : "https://mangadex.org/chapter/74149a55-e7c4-44ea-8a37-98e879c1096f",
    "#comment" : "MANGA Plus (#1154)",
    "#category": ("", "mangadex", "chapter"),
    "#class"   : mangadex.MangadexChapterExtractor,
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://mangadex.org/chapter/364728a4-6909-4164-9eea-6b56354f7c78",
    "#comment" : "'externalUrl', but still downloadable / 404 (#2503)",
    "#category": ("", "mangadex", "chapter"),
    "#class"   : mangadex.MangadexChapterExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://mangadex.org/title/f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
    "#comment" : "mutliple values for 'lang' (#4093)",
    "#category": ("", "mangadex", "manga"),
    "#class"   : mangadex.MangadexMangaExtractor,
    "#count"   : ">= 5",

    "manga"        : "Souten no Koumori",
    "manga_id"     : "f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
    "title"        : r"re:One[Ss]hot",
    "volume"       : 0,
    "chapter"      : 0,
    "chapter_minor": "",
    "chapter_id"   : str,
    "date"         : datetime.datetime,
    "lang"         : str,
    "language"     : str,
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
    "#category": ("", "mangadex", "manga"),
    "#class"   : mangadex.MangadexMangaExtractor,
    "#options" : {"lang": "fr,it"},
    "#count"   : 2,

    "manga"   : "Souten no Koumori",
    "lang"    : {"fr", "it"},
    "language": {"French", "Italian"},
},

{
    "#url"     : "https://mangadex.cc/manga/d0c88e3b-ea64-4e07-9841-c1d2ac982f4a/",
    "#category": ("", "mangadex", "manga"),
    "#class"   : mangadex.MangadexMangaExtractor,
    "#options" : {"lang": "en"},
    "#count"   : ">= 100",
},

{
    "#url"     : "https://mangadex.org/title/7c1e2742-a086-4fd3-a3be-701fd6cf0be9",
    "#category": ("", "mangadex", "manga"),
    "#class"   : mangadex.MangadexMangaExtractor,
    "#count"   : ">= 25",
},

{
    "#url"     : "https://mangadex.org/title/584ef094-b2ab-40ce-962c-bce341fb9d10",
    "#category": ("", "mangadex", "manga"),
    "#class"   : mangadex.MangadexMangaExtractor,
    "#count"   : ">= 20",
},

{
    "#url"     : "https://mangadex.org/title/feed",
    "#category": ("", "mangadex", "feed"),
    "#class"   : mangadex.MangadexFeedExtractor,
},

{
    "#url"     : "https://mangadex.org/list/3a0982c5-65aa-4de2-8a4a-2175be7383ab/test",
    "#category": ("", "mangadex", "list"),
    "#class"   : mangadex.MangadexListExtractor,
    "#urls"    : (
        "https://mangadex.org/title/cba4e5d6-67a0-47a0-b37a-c06e9bf25d93",
        "https://mangadex.org/title/cad76ec6-ca22-42f6-96f8-eca164da6545",
    ),
},

{
    "#url"     : "https://mangadex.org/list/3a0982c5-65aa-4de2-8a4a-2175be7383ab/test?tab=titles",
    "#category": ("", "mangadex", "list"),
    "#class"   : mangadex.MangadexListExtractor,
},

{
    "#url"     : "https://mangadex.org/list/3a0982c5-65aa-4de2-8a4a-2175be7383ab/test?tab=feed",
    "#category": ("", "mangadex", "list-feed"),
    "#class"   : mangadex.MangadexListExtractor,
    "#urls"    : (
        "https://mangadex.org/chapter/fa8a695d-260f-4dcc-95a3-1f30e66d6571",
        "https://mangadex.org/chapter/c765d6d5-5712-4360-be0b-0c8e0914fc94",
        "https://mangadex.org/chapter/788766b9-41c6-422e-97ba-552f03ba9655",
    ),
},

{
    "#url"     : "https://mangadex.org/author/7222d0d5-836c-4bf3-9174-72bceade8c87/kotoyama",
    "#class"   : mangadex.MangadexAuthorExtractor,
    "#urls"    : (
        "https://mangadex.org/title/259dfd8a-f06a-4825-8fa6-a2dcd7274230",
        "https://mangadex.org/title/d0c88e3b-ea64-4e07-9841-c1d2ac982f4a",
        "https://mangadex.org/title/f48bbb5f-8a23-4dea-8177-eb2dbbcbf4fa",
        "https://mangadex.org/title/00b68132-4e69-4ff9-ad4b-29138b377dc8",
        "https://mangadex.org/title/f1b70bba-3873-4c22-afa3-1d1c78299cd9",
        "https://mangadex.org/title/41cd6fa7-3e53-4900-88e6-4a06cd7df9ad",
    ),
},

{
    "#url"     : "https://mangadex.org/author/254efca2-0ac0-432c-a3a3-55b7e207e87d/flipflops",
    "#class"   : mangadex.MangadexAuthorExtractor,
    "#pattern" : mangadex.MangadexMangaExtractor.pattern,
    "#options" : {"lang": "en"},
    "#count"   : ">= 15",
},

)
