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

    "filename" : str,
    "extension": "webp",
    "width"    : 1424,
    "height"   : 2000,
    "size"     : range(67460, 276608),
    "optimized": {int, None},

    "volume": 1,
    "chapter": 10,
    "chapter_minor": ".5",
    "chapter_hid": "L7TaJB4n",
    "chapter_id": 4105343,
    "chapter_string": "L7TaJB4n-chapter-10.5-en",
    "count": 5,
    "page" : range(1, 5),
    "date": "dt:2025-06-21 13:07:32",
    "date_updated": "type:datetime",
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
    "rank": range(29_000, 32_000),
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
    "date_updated": "type:datetime",
    "demographic": "Seinen",
    "description": str,
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
        "amz": "https://www.amazon.co.jp/dp/B0F2SL834T",
        "bw" : "series/520105",
        "mal": "178605",
        "raw": "https://manga.nicovideo.jp/comic/71123",
    },
    "manga": "Koko Jidai ni Gomandatta Jou sama to no Dousei Seikatsu wa Igaito Igokochi ga Warukunai",
    "manga_hid": "oeb0Dydj",
    "manga_id": 114526,
    "manga_slug": "koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai",
    "manga_titles": "len:list:4",
    "mature": True,
    "origin": "ja",
    "published": 2025,
    "publisher": ["Suiyoubi wa Mattari Dash X Comic"],
    "rank": range(100, 1000),
    "rating": "suggestive",
    "score": float,
    "status": "Ongoing",
    "tags" : list,
    "theme": ["School Life"],
    "title": "Yamamoto \"Đuổi\" Hayashi Đi Ư!?",
},

{
    "#url"     : "https://comick.io/comic/00-the-100-girlfriends-who-really-really-really-really-really-love-you/Zqu59ZKD",
    "#comment" : "no chapter info (#7972)",
    "#class"   : comick.ComickChapterExtractor,
    "#pattern" : r"https://meo.comick.pictures/\d+-[\w-]+\.(jpg|png)",
    "#count"   : 22,

    "artist"        : ["Nozawa Yukiko"],
    "author"        : ["Nakamura Rikito"],
    "chapter"       : 0,
    "chapter_hid"   : "Zqu59ZKD",
    "chapter_id"    : 3437106,
    "chapter_minor" : "",
    "chapter_string": "Zqu59ZKD",
    "count"         : 22,
    "date"          : "dt:2024-08-29 14:20:51",
    "date_updated"  : "dt:2024-08-29 14:20:51",
    "group"         : ["ENCHILADAS NO SEKAI"],
    "lang"          : "es-419",
    "manga"         : "The 100 Girlfriends Who Really, Really, Really, Really, Really Love You",
    "manga_hid"     : "grNTmie1",
    "manga_id"      : 37955,
    "manga_slug"    : "00-the-100-girlfriends-who-really-really-really-really-really-love-you",
    "published"     : 2019,
    "publisher"     : ["Shueisha"],
    "title"         : "MAI Y MOMOHA SE CONVIERTEN EN MAIDS CERTIFICADAS(TAL VEZ)",
    "volume"        : 0,
},

{
    "#url"     : "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon",
    "#comment" : "all chapters",
    "#class"   : comick.ComickMangaExtractor,
    "#pattern" : comick.ComickChapterExtractor.pattern,
    "#count"   : range(890, 1000),
},

{
    "#url"     : "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon?lang=pt-br&group=Amadeus+Scans&chap-order=&date-order=1&page=3#chapter-header",
    "#comment" : "query parameters",
    "#class"   : comick.ComickMangaExtractor,
    "#pattern" : comick.ComickChapterExtractor.pattern,
    "#results" : (
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/It8UGI_U-chapter-137-pt-br",
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/YlHNac8_-chapter-138-pt-br",
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/dnMuDUdy-chapter-139-pt-br",
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/1oFGBeum-chapter-140-pt-br",
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/_lIICVw3-chapter-141-pt-br",
    ),

    "lang": "pt-br",
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
        "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai/nhtKNBiS-chapter-5-vi",
        "https://comick.io/comic/koko-jidai-ni-gomandatta-jou-sama-to-no-dousei-seikatsu-wa-igaito-igokochi-ga-warukunai/1ukj8pOy-chapter-6-vi",
    ),

    "lang": "vi",
},

{
    "#url"     : "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon",
    "#comment" : "'lang' option (#7938)",
    "#class"   : comick.ComickMangaExtractor,
    "#options" : {"lang": ["fr", "id"]},
    "#pattern" : comick.ComickChapterExtractor.pattern,
    "#results" : (
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/l0Mj1-chapter-1-id",
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/xnkNn-chapter-1-fr",
        "https://comick.io/comic/kobayashi-san-chi-no-maid-dragon/vw9Kn-chapter-2-id",
    ),

    "lang": {"fr", "id"},
},

{
    "#url"     : "https://comick.io/comic/00-the-100-girlfriends-who-really-really-really-really-really-love-you?lang=es-419&chap-order=1&date-order=",
    "#comment" : "chapter without chapter info (#7972)",
    "#class"   : comick.ComickMangaExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://comick.io/comic/00-the-100-girlfriends-who-really-really-really-really-really-love-you/Zqu59ZKD",
        "https://comick.io/comic/00-the-100-girlfriends-who-really-really-really-really-really-love-you/y6kgR-chapter-1-es-419",
        "https://comick.io/comic/00-the-100-girlfriends-who-really-really-really-really-really-love-you/wkMZr-chapter-1-es-419",
    ),

    "chapter": {0, 1},
    "lang"   : "es-419",
},

)
