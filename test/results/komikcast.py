# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import komikcast


__tests__ = (
{
    "#url"     : "https://komikcast.lol/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#category": ("", "komikcast", "chapter"),
    "#class"   : komikcast.KomikcastChapterExtractor,
    "#pattern" : r"https://svr\d+\.imgkc\d+\.my\.id/wp-content/img/A/Apotheosis/002-2/\d{3}\.jpg",
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
    "#category": ("", "komikcast", "chapter"),
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.me/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#category": ("", "komikcast", "chapter"),
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.com/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#category": ("", "komikcast", "chapter"),
    "#class"   : komikcast.KomikcastChapterExtractor,
},

{
    "#url"     : "https://komikcast.me/chapter/soul-land-ii-chapter-300-1-bahasa-indonesia/",
    "#category": ("", "komikcast", "chapter"),
    "#class"   : komikcast.KomikcastChapterExtractor,
    "#sha1_url"     : "f2674e31b41a7f009f2f292652be2aefb6612d3f",
    "#sha1_metadata": "cb646cfed3d45105bd645ab38b2e9f7d8c436436",
},

{
    "#url"     : "https://komikcast.site/komik/090-eko-to-issho/",
    "#category": ("", "komikcast", "manga"),
    "#class"   : komikcast.KomikcastMangaExtractor,
    "#sha1_url"     : "19d3d50d532e84be6280a3d61ff0fd0ca04dd6b4",
    "#sha1_metadata": "837a7e96867344ff59d840771c04c20dc46c0ab1",
},

{
    "#url"     : "https://komikcast.me/tonari-no-kashiwagi-san/",
    "#category": ("", "komikcast", "manga"),
    "#class"   : komikcast.KomikcastMangaExtractor,
},

)
