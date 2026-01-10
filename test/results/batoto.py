# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import batoto

__tests__ = (
{
    "#url"     : "https://battwo.com/title/86408-i-shall-master-this-family-official/1681030-ch_8",
    "#class"   : batoto.BatotoChapterExtractor,
    "#pattern" : r"https://n\d+\.mb\w{3}\.org/media/7006/.+\.webp",
    "#count"   : 66,

    "artist"        : ["Mon"],
    "author"        : ["Kim Roah"],
    "chapter"       : 8,
    "chapter_id"    : 1681030,
    "chapter_minor" : "",
    "chapter_string": "Chapter 8",
    "chapter_url"   : "8",
    "count"         : 66,
    "page"          : range(1, 66),
    "cover"         : "https://n24.mbhiz.org/media/mbim/476/4765b5482c87970ae18e3e335bc8a3f2f7a47f8b_400_600_43900.webp",
    "date"          : "dt:2021-05-15 18:51:37",
    "description"   : "The great Lombardi family was once at the top of the empire. After the death of its patriarch, the fate of the family and that of Firentia, born from a Lombardi and a peasant, fall to ruin at the hands of her useless and cruel cousins. But when she’s reincarnated as her seven-year-old self, she’ll work to protect the family’s honor, gain her grandpa Lulac’s favor, and prevent her own father’s death. In this lifetime, there’s only one way for her to win: become the head of their mighty household.",
    "extension"     : "webp",
    "filename"      : str,
    "lang"          : "en",
    "lang_orig"     : "ko",
    "manga"         : "I Shall Master this Family! [Official]",
    "manga_date"    : "dt:2021-05-10 20:18:58",
    "manga_date_updated": "dt:2025-12-28 18:41:24",
    "manga_id"      : 86408,
    "manga_slug"    : "i-shall-master-this-family-official",
    "published"     : "2021",
    "score"         : range(8, 10),
    "status"        : "ongoing",
    "title"         : "Observing",
    "uploader"      : "677083",
    "volume"        : 0,
    "genre"         : [
        "drama",
        "fantasy",
        "full color",
        "historical",
        "manhwa",
        "reincarnation",
        "romance",
        "shoujo",
        "time travel",
        "webtoon",
    ],
},

{
    "#url"     : "https://battwo.com/title/104929-86-eighty-six-official/1943513-vol_1-ch_5",
    "#comment" : "volume (vol) in url",
    "#class"   : batoto.BatotoChapterExtractor,
    "#count"   : 7,

    "manga"  : "86--EIGHTY-SIX (Official)",
    "title"  : "The Spearhead Squadron's Power",
    "volume" : 1,
    "chapter": 5,
},

{
    "#url"     : "https://mto.to/chapter/2584460",
    "#comment" : "'-' in manga title (#5200)",
    "#class"   : batoto.BatotoChapterExtractor,

    "chapter"   : 9,
    "chapter_id": 2584460,
    "chapter_minor": "",
    "chapter_url": "9",
    "count"     : 18,
    "date"      : "dt:2023-11-26 11:01:12",
    "manga"     : "Isekai Teni shitara Aiken ga Saikyou ni narimashita - Silver Fenrir to Ore ga Isekai Kurashi wo Hajimetara (Official)",
    "manga_id"  : 126793,
    "title"     : "",
    "volume"    : 0
},

{
    "#url"     : "https://battwo.com/title/90710-new-suitor-for-the-abandoned-wife/2089747-ch_76",
    "#comment" : "duplicate info in chapter_minor / title (#5988)",
    "#class"   : batoto.BatotoChapterExtractor,

    "chapter"      : 76,
    "chapter_id"   : 2089747,
    "chapter_minor": "",
    "chapter_url"  : "76",
    "title"        : "Side Story 4 [END]",
},

{
    "#url"     : "https://battwo.com/title/115494-today-with-you/2631897-ch_38",
    "#class"   : batoto.BatotoChapterExtractor,

    "chapter"       : 37,
    "chapter_id"    : 2631897,
    "chapter_minor" : "",
    "chapter_string": "S1 Episode 37 (End of season)",
    "chapter_url"   : "38",
    "count"         : 69,
    "date"          : "dt:2023-12-20 17:31:18",
    "manga"         : "Today With You",
    "manga_id"      : 115494,
    "title"         : "",
    "volume"        : 1,
},

{
    "#url"     : "https://battwo.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://battwo.com/chapter/1681030",
    "#comment" : "v2 URL",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://battwo.com/title/113742-futsutsuka-na-akujo-de-wa-gozaimasu-ga-suuguu-chouso-torikae-den-official",
    "#class"   : batoto.BatotoMangaExtractor,
    "#pattern" : batoto.BatotoChapterExtractor.pattern,
    "#count"   : range(50, 80),
    "#options" : {"domain": "xbato.org"},

    "author"       : ["Satsuki Nakamura"],
    "artist"       : ["Ei Ohitsuji", "Kana Yuki"],
    "chapter"      : int,
    "chapter_minor": {"", ".5", ".6", ".7", ".8", ".9"},
    "cover"        : "https://k02.mbimg.org/media/mbim/aa0/aa011e00e8354783114e1eb26beee624b98ab7f7_600_843_172402.webp",
    "date"         : "type:datetime",
    "description"  : "As the crown prince’s favored maiden at court, Kou Reirin’s future as the next empress is all but assured. That is, until her rival Shu Keigetsu, the court’s “sewer rat,” pushes her over a balcony! Reirin survives, but wakes up in Keigetsu’s body! Turns out, Keigetsu has used magic to swap bodies with Reirin in order to steal her position at court. After being sickly her whole life, Reirin is determined to use this new body to turn things around. She won’t let anything stop her, not even her impending execution!",
    "lang"         : "en",
    "lang_orig"    : "ja",
    "manga"        : "Futsutsuka na Akujo de wa Gozaimasu ga - Suuguu Chouso Torikae Den",
    "manga_date"   : "dt:2022-11-07 09:10:20",
    "manga_date_updated": "type:datetime",
    "manga_id"     : 113742,
    "manga_slug"   : "futsutsuka-na-akujo-de-wa-gozaimasu-ga-suuguu-chouso-torikae-den",
    "published"    : "2020",
    "score"        : range(8, 10),
    "status"       : "ongoing",
    "uploader"     : "713741",
    "genre"        : [
        "adaptation",
        "bodyswap",
        "drama",
        "fantasy",
        "historical",
        "josei",
        "manga",
        "romance",
        "villainess",
    ],
},

{
    "#url"     : "https://battwo.com/title/104929-86-eighty-six-official",
    "#comment" : "Manga with number in name",
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 18",

    "manga": "86--EIGHTY-SIX (Official)",
},

{
    "#url"     : "https://battwo.com/title/140046-the-grand-duke-s-fox-princess-mgchan",
    "#comment" : "Non-English translation (Indonesian)",
    "#class"   : batoto.BatotoMangaExtractor,
    "#count"   : ">= 29",

    "manga": "The Grand Duke’s Fox Princess [cont by LUNABY]",
},

{
    "#url"     : "https://battwo.com/title/134270-removed",
    "#comment" : "Deleted/removed manga",
    "#class"   : batoto.BatotoMangaExtractor,
    "#log"     : "'This comic has been marked as deleted and the chapter list is not available.'",
    "#count"   : 0,
},

{
    "#url"     : "https://mto.to/series/136193",
    "#comment" : "uploader notice (#7657)",
    "#category": ("", "batoto", "manga"),
    "#class"   : batoto.BatotoMangaExtractor,
    "#log"     : "'UPLOADER NOTICE - The comic was deleted off EbookRenta :/'",
    "#results" : (
        "https://mto.to/title/136193-botsuraku-sunzen-desunode-konyakusha-o-furikiro-to-omoimasu-official/2456573-ch_1",
        "https://mto.to/title/136193-botsuraku-sunzen-desunode-konyakusha-o-furikiro-to-omoimasu-official/2713985-ch_2",
        "https://mto.to/title/136193-botsuraku-sunzen-desunode-konyakusha-o-furikiro-to-omoimasu-official/2739046-ch_3",
    ),
},

{
    "#url"     : "https://battwo.com/title/86408-i-shall-master-this-family-official",
    "#class"   : batoto.BatotoMangaExtractor,
},

{
    "#url"     : "https://battwo.com/series/86408/i-shall-master-this-family-official",
    "#comment" : "v2 URL",
    "#class"   : batoto.BatotoMangaExtractor,
},

{
    "#url"     : "https://dto.to/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://fto.to/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://hto.to/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://jto.to/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://mto.to/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://wto.to/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://mangatoto.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://mangatoto.net/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://mangatoto.org/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://batocomic.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://batocomic.net/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://batocomic.org/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://readtoto.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://readtoto.net/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://readtoto.org/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://xbato.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://xbato.net/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://xbato.org/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://zbato.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://zbato.net/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://zbato.org/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://comiko.net/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://comiko.org/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

{
    "#url"     : "https://batotoo.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://batotwo.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},
{
    "#url"     : "https://battwo.com/title/86408/1681030",
    "#class"   : batoto.BatotoChapterExtractor,
},

)
