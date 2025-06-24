# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import comick


__tests__ = (

{
    "#url"     : "https://comick.io/comic/neko-no-oshigoto/L7TaJB4n-chapter-10.5-en",
    "#class"   : comick.ComickChapterExtractor,
    "#results" : (
        "https://meo.comick.pictures/0-ThqKs6imRo5oK.webp",
        "https://meo.comick.pictures/1-NHbu8c09NjBCv.webp",
        "https://meo.comick.pictures/2-i88d48rBYweD0.webp",
        "https://meo.comick.pictures/3-AKTIcb3vjy3Lf.webp",
        "https://meo.comick.pictures/4-N8Vj2XVdYY4Pv.webp",
    ),

    "volume": 1,
    "chapter": 10,
    "chapter_minor": ".5",
    "chapter_hid": "L7TaJB4n",
    "chapter_id": 4105343,
    "chapter_string": "L7TaJB4n-chapter-10.5-en",
    "count": 5,
    "page" : range(1, 5),
    "date": "dt:2025-06-21 13:07:32",
    "date_updated": "dt:2025-06-21 16:52:40",
    "demographic": "Seinen",
    "description": "Ever wondered what it would be like if your cat had to get a job? The cats in this book do every kind of occupation you can imagine, and they do it just the way they like. Feline chefs, dentists, wrestlers, detectives, opera singers and much more await in this hilarious full-color collection!",
    "format": "Full Color",
    "lang": "en",
    "manga": "Neko no Oshigoto",
    "manga_hid": "aHgHjCfY",
    "manga_id": 119004,
    "manga_slug": "neko-no-oshigoto",
    "mature": False,
    "origin": "ja",
    "published": 2023,
    "publisher": (),
    "rank": 29915,
    "rating": "safe",
    "score": float,
    "status": "Ongoing",
    "title": "",

    "tags"  : (),
    "artist": ["Pandania"],
    "author": ["Pandania"],
    "group" : ["Official"],
    "theme" : ["Animals"],

    "genre" : [
        "Comedy",
        "Slice of Life",
    ],
    "manga_titles": [
        "ねこのおしごと",
        "Cats With Jobs",
    ],
    "links": {
        "al"   : "194211",
        "amz"  : "https://www.amazon.co.jp/%E3%81%AD%E3%81%93%E3%81%AE%E3%81%8A%E3%81%97%E3%81%94%E3%81%A8-1-%E3%83%92%E3%83%BC%E3%83%AD%E3%83%BC%E3%82%BA%E3%82%B3%E3%83%9F%E3%83%83%E3%82%AF%E3%82%B9-%E3%82%8F%E3%81%84%E3%82%8B%E3%81%A9-%E3%81%B1%E3%82%93%E3%81%A0%E3%81%AB%E3%81%82/dp/4864681643",
        "bw"   : "series/409260/list",
        "ebj"  : "https://ebookjapan.yahoo.co.jp/books/754652/",
        "engtl": "https://sevenseasentertainment.com/series/cats-with-jobs/",
    },
},

{
    "#url"     : "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai/aPu5CgJA-chapter-3-vi",
    "#class"   : comick.ComickChapterExtractor,
    "#pattern" : r"https://meo.comick.pictures/\d+-[\w-]+\.(jpg|png)",
    "#count"   : 20,

    "artist": ["Togawa Ritsu"],
    "author": ["Dozaemon Misoneta"],
    "volume": 1,
    "chapter": 3,
    "chapter_minor": "",
    "chapter_hid": "aPu5CgJA",
    "chapter_id": 4043238,
    "chapter_string": "aPu5CgJA-chapter-3-vi",
    "count": 20,
    "date": "dt:2025-05-09 17:25:38",
    "date_updated": "dt:2025-06-21 18:25:55",
    "demographic": "Seinen",
    "description": "\"Hey, wanna do it?\"\n\nA romantic comedy about living together with a scarred \"Queen\" in a relationship that’s more than friends but less than lovers!!\n\nOne late night, Yamamoto, a college student working part-time at a convenience store, reunites with Hayashi Megumi, his high school classmate and the most beautiful girl in their class.\nKnown as the \"Queen\" for her strong-willed and arrogant personality, Yamamoto had always found her difficult to get along with. However, during a routine conversation, he notices painful bruises on her wrist.\nAfter learning that her boyfriend had been abusing her, Yamamoto decides to let Hayashi stay at his place...!?",
    "format": "Adaptation",
    "genre": [
        "Comedy",
        "Drama",
        "Mystery",
        "Psychological",
        "Romance",
    ],
    "group": [
        "Dịch cho vui",
    ],
    "lang": "vi",
    "links": {
        "al" : "187656",
        "amz": "https://www.amazon.co.jp/-/en/dp/4088937163",
        "bw" : "series/520105/list",
        "mal": "178605",
        "raw": "https://manga.nicovideo.jp/comic/71123",
    },
    "manga": "Koko Jidai ni Gomandatta Jou sama to no Dousei Seikatsu wa Igaito Igokochi ga Warukunai",
    "manga_hid": "oeb0Dydj",
    "manga_id": 114526,
    "manga_slug": "koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai",
    "manga_titles": [
        "Cuộc sống chung với nữ hoàng từng kiêu ngạo hồi cấp ba, không ngờ lại khá dễ chịu.",
        "高校時代に傲慢だった女王様との同棲生活は意外と居心地が悪くない",
        "Koko Jidai Ni Gomandatta Jou Sama To No Dosei Seikatsu Ha Igaito Igokochi Ga Warukunai",
        "Living together with the queen from my high school days who was arrogant, surprisingly isn't that uncomfortable",
    ],
    "mature": False,
    "origin": "ja",
    "published": 2025,
    "publisher": (),
    "rank": range(800, 1000),
    "rating": "safe",
    "score": float,
    "status": "Ongoing",
    "tags" : (),
    "theme": ["School Life"],
    "title": "Yamamoto \"Đuổi\" Hayashi Đi Ư!?",
},

{
    "#url"     : "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai?lang=vi",
    "#comment" : "language filter",
    "#class"   : comick.ComickMangaExtractor,
    "#pattern" : comick.ComickChapterExtractor.pattern,
    "#results" : (
        "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai/1ngqqSQg-chapter-1-vi",
        "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai/rSROPoui-chapter-2-vi",
        "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai/aPu5CgJA-chapter-3-vi",
        "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai/eQ26SPqi-chapter-4-vi",
    ),

    "lang": "vi",
},

)
