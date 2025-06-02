# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import komikcast


__tests__ = (
{
    "#url"     : "https://komikcast.lol/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#class"   : komikcast.KomikcastChapterExtractor,
    "#pattern" : r"https://svr?\d+\.imgkc\d+\.my\.id/wp-content/img/A/Apotheosis/002-2/\d{3}\.jpg",
    "#count"   : 18,

    "chapter"  : 2,
    "chapter_minor": ".2",
    "count"    : 18,
    "extension": "jpg",
    "filename" : r"re:0\d{2}",
    "lang"     : "id",
    "language" : "Indonesian",
    "manga"    : "Apotheosis",
    "page"     : range(1, 18),
    "title"    : "",
},

{
    "#url"     : "https://komikcast.site/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.me/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.com/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.cz/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.la/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.me/chapter/soul-land-ii-chapter-300-1-bahasa-indonesia/",
    "#class"   : komikcast.KomikcastChapterExtractor,
    "#pattern" : r"https://svr?\d\.imgkc\d*\.my\.id/wp-content/img/S/Soul_Land_II/300\.1/\d\d\.jpg",
    "#count"   : 9,
    "#sha1_metadata": "cb646cfed3d45105bd645ab38b2e9f7d8c436436",
},

{
    "#url"     : "https://komikcast.site/komik/090-eko-to-issho/",
    "#class"   : komikcast.KomikcastMangaExtractor,
    "#pattern" : komikcast.KomikcastChapterExtractor.pattern,
    "#count"   : 12,

    "author" : "Asakura Maru",
    "chapter": range(1, 12),
    "chapter_minor": "",
    "genres" : [
        "Comedy",
        "Drama",
        "Romance",
        "School Life",
        "Sci-Fi",
        "Shounen"
    ],
    "manga"  : "090 Eko to Issho",
    "type"   : "Manga",
},

{
    "#url"     : "https://komikcast.me/tonari-no-kashiwagi-san/",
    "#class"   : komikcast.KomikcastMangaExtractor,
},

)
