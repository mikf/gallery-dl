# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import komikcast


__tests__ = (
{
    "#url"     : "https://komikcast.site/chapter/apotheosis-chapter-02-2-bahasa-indonesia/",
    "#category": ("", "komikcast", "chapter"),
    "#class"   : komikcast.KomikcastChapterExtractor,
    "#sha1_url"     : "f6b43fbc027697749b3ea1c14931c83f878d7936",
    "#sha1_metadata": "f3938e1aff9ad1f302f52447e9781b21f6da26d4",
},

{
    "#url"     : "https://komikcast.me/chapter/soul-land-ii-chapter-300-1-bahasa-indonesia/",
    "#category": ("", "komikcast", "chapter"),
    "#class"   : komikcast.KomikcastChapterExtractor,
    "#sha1_url"     : "efd00a9bd95461272d51990d7bc54b79ff3ff2e6",
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
