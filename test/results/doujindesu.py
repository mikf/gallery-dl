# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import doujindesu

__tests__ = (
    # Test chapter extractor
    {
        "#url"     : "https://doujindesu.tv/the-hotties-good-at-football-chapter-03/",
        "#class"   : doujindesu.DoujindesuChapterExtractor,
        "#pattern" : r"https://desu\.photos/(uploads|storage)/.+\.(jpg|jpeg|png|webp)",
        "#count"   : 30,

        "chapter"  : 3,
        "chapter_minor": "",
        "manga"    : "The Hottie's Good at Football",
        "lang"     : "id",
        "language" : "Indonesian",
        "extension": r"(jpg|jpeg|png|webp)",
    },

    # Test manga extractor (list of chapters)
    {
        "#url"     : "https://doujindesu.tv/manga/duplex-house/",
        "#class"   : doujindesu.DoujindesuMangaExtractor,
        "#pattern" : doujindesu.DoujindesuChapterExtractor.pattern,
        "#count"   : 50,  # Sesuaikan perkiraan jumlah chapter

        "manga"    : "Duplex House",
    },

    # Test single non-chapter post
    {
        "#url"     : "https://doujindesu.tv/2020/07/19/chop-stick/",
        "#class"   : doujindesu.DoujindesuChapterExtractor,
        "#pattern" : r"https://desu\.photos/(uploads|storage)/.+\.(jpg|jpeg|png|webp)",
        "#count"   : 5,

        "manga"    : "CHOP STICK",
        "chapter"  : None,
    },
)
