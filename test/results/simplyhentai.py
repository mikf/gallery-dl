# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import simplyhentai


__tests__ = (
{
    "#url"     : "https://www.simply-hentai.com/puella-magi-madoka-magica/hangyaku-no-hanafuda-monogatari-english",
    "#class"   : simplyhentai.SimplyhentaiGalleryExtractor,
    "#pattern" : r"https://images\.sh\-cdn\.com/0/c/1/e/365291/\w+\.jpg",
    "#count"   : 25,

    "artists"        : [],
    "comment_count"  : int,
    "count"          : 25,
    "cover"          : "https://images.sh-cdn.com/0/c/1/e/365291/1f47ed30.jpg",
    "created_at"     : "2024-01-07T15:03:11.924+01:00",
    "date"           : "dt:2024-01-07 14:03:11",
    "description"    : None,
    "extension"      : "jpg",
    "filename"       : str,
    "gallery_id"     : 365291,
    "id"             : int,
    "image_count"    : 25,
    "lang"           : "en",
    "language"       : "English",
    "new"            : False,
    "num"            : range(1, 25),
    "other_languages": [],
    "parodies"       : ["Puella Magi Madoka Magica"],
    "reactions"      : {},
    "redirected"     : False,
    "series"         : "Puella Magi Madoka Magica",
    "slug"           : "hangyaku-no-hanafuda-monogatari-english",
    "title"          : "Hangyaku no Hanafuda Monogatari [English}",
    "translators"    : [],
    "type"           : "Album",
    "user"           : None,
    "views"          : range(80_000, 500_000),
    "characters"     : [
        "homura akemi",
        "kyouko sakura",
        "madoka kaname",
        "mami tomoe",
        "sayaka miki",
    ],
    "tags"           : [
        "females only",
        "Giantess",
        "Kimono",
        "Yuri",
    ],
    "anijunky"       : dict,
    "interactions"   : dict,
    "!related"       : dict,
    "!images"        : list,
    "!pages"         : list,
},

{
    "#url"     : "https://www.simply-hentai.com/dungeon-ni-deai-o-motomeru-no-wa-machigatteiru-darou-ka/aisha-defeated-by-bell",
    "#comment" : "12 or less pages",
    "#class"   : simplyhentai.SimplyhentaiGalleryExtractor,
    "#pattern" : r"https://images\.sh\-cdn\.com/f/0/6/6/364253/\w+\.jpg",
    "#count"   : 11,

    "artists"        : ["bareisho tarou"],
    "count"          : 11,
    "cover"          : "https://images.sh-cdn.com/f/0/6/6/364253/a313a9ae.jpg",
    "date"           : "dt:2023-12-11 07:14:11",
    "gallery_id"     : 364253,
    "id"             : int,
    "lang"           : "en",
    "parodies"       : ["dungeon ni deai o motomeru no wa machigatteiru darou ka"],
    "series"         : "dungeon ni deai o motomeru no wa machigatteiru darou ka",
    "title"          : "Aisha Defeated By Bell",
    "characters"     : [
        "aisha belka",
        "bell cranel",
        "haruhime sanjouno",
    ],
    "tags"           : [
        "big breasts",
        "big penis",
        "Dark Skin",
        "Fox Girl",
        "Harem",
        "Impregnation",
        "kemonomimi | animal ears",
        "Kimono",
        "multi-work series",
        "Nakadashi",
        "Pregnant",
        "Prostitution",
        "sole female",
        "sole male",
        "very long hair",
    ],
},

{
    "#url"     : "https://www.simply-hentai.com/series/mysterious-girlfriend-x",
    "#class"   : simplyhentai.SimplyhentaiSeriesExtractor,
    "#results" : (
        "https://www.simply-hentai.com/mysterious-girlfriend-x/sekkyokuteki-na-kanojo-b2d61",
        "https://www.simply-hentai.com/mysterious-girlfriend-x/sekkyokuteki-na-kanojo-30cd3",
        "https://www.simply-hentai.com/mysterious-girlfriend-x/sekkyokuteki-na-kanojo",
        "https://www.simply-hentai.com/mysterious-girlfriend-x/urabe-to-shitemita",
    ),
},

{
    "#url"     : "https://www.simply-hentai.com/series/mysterious-girlfriend-x/tag-nakadashi/sort-popularity",
    "#class"   : simplyhentai.SimplyhentaiSeriesExtractor,
    "#results" : (
        "https://www.simply-hentai.com/mysterious-girlfriend-x/sekkyokuteki-na-kanojo",
        "https://www.simply-hentai.com/mysterious-girlfriend-x/urabe-to-shitemita",
    ),
},

{
    "#url"     : "https://www.simply-hentai.com/series/mysterious-girlfriend-x?filter%5Btags%5D%5B0%5D=schoolgirl%20uniform&filter%5Btags%5D%5B1%5D=Nakadashi&filter%5Bparodies%5D%5B0%5D=Nazo%20no%20Kanojo%20X",
    "#class"   : simplyhentai.SimplyhentaiSeriesExtractor,
    "#results" : "https://www.simply-hentai.com/mysterious-girlfriend-x/sekkyokuteki-na-kanojo",
},

{
    "#url"     : "https://www.simply-hentai.com/2-mangas",
    "#class"   : simplyhentai.SimplyhentaiMangaExtractor,
    "#pattern" : simplyhentai.SimplyhentaiGalleryExtractor.pattern,
    "#range"   : "1-5",
},

{
    "#url"     : "https://www.simply-hentai.com/2-mangas/sort-most-viewed",
    "#class"   : simplyhentai.SimplyhentaiMangaExtractor,
    "#range"   : "1-5",
    "#results" : (
        "https://www.simply-hentai.com/8-original-work/1-ikura-de-yaremasu-ka-a0031",
        "https://www.simply-hentai.com/8-naruto/3-konoha-genei-jutsu",
        "https://www.simply-hentai.com/8-naruto/3-erokosu-vol14",
        "https://www.simply-hentai.com/2-dragon-ball-super/3-special-training",
        "https://www.simply-hentai.com/8-naruto/3-hinata-fight",
    ),
},

{
    "#url"     : "https://www.simply-hentai.com/language/polish",
    "#class"   : simplyhentai.SimplyhentaiLanguageExtractor,
    "#results" : (
        "https://www.simply-hentai.com/chrono-trigger/lucca-no-hikigane-luccas-trigger",
        "https://www.simply-hentai.com/sword-art-online/omodume-box-xxiii",
        "https://www.simply-hentai.com/8-original-work/sdpo-seimukan-no-susume-6bedc",
    ),
},

{
    "#url"     : "https://www.simply-hentai.com/language/german/sort-newest/page-12",
    "#class"   : simplyhentai.SimplyhentaiLanguageExtractor,
    "#pattern" : simplyhentai.SimplyhentaiGalleryExtractor.pattern,
    "#count"   : 12,
},

{
    "#url"     : "https://www.simply-hentai.com/parody/touhou",
    "#class"   : simplyhentai.SimplyhentaiTagExtractor,
},

{
    "#url"     : "https://www.simply-hentai.com/tag/1-sole-female",
    "#class"   : simplyhentai.SimplyhentaiTagExtractor,
},

{
    "#url"     : "https://www.simply-hentai.com/character/producer",
    "#class"   : simplyhentai.SimplyhentaiTagExtractor,
},

{
    "#url"     : "https://www.simply-hentai.com/collection/english-b5e31",
    "#class"   : simplyhentai.SimplyhentaiTagExtractor,
    "#results" : (
        "https://www.simply-hentai.com/8-original-work/i_did_naughty_things_with_my__sister",
        "https://www.simply-hentai.com/8-original-work/suki-suki-daisuki-onee-chan-i-love-love-love-you-onee-chan",
        "https://www.simply-hentai.com/2-detective-conan/13303-f-l-o-w-e-r-03",
    ),
},

{
    "#url"     : "https://www.simply-hentai.com/artist/crimson-carmine/tag-color/sort-alphabetical",
    "#class"   : simplyhentai.SimplyhentaiTagExtractor,
    "#pattern" : simplyhentai.SimplyhentaiGalleryExtractor.pattern,
    "#count"   : 25,
},

{
    "#url"     : "https://www.simply-hentai.com/translator/10-team-vanilla",
    "#class"   : simplyhentai.SimplyhentaiTagExtractor,
},

)
