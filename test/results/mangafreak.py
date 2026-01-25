# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangafreak


__tests__ = (
{
    "#url"     : "https://ww2.mangafreak.me/Read1_Onepunch_Man_1",
    "#class"   : mangafreak.MangafreakChapterExtractor,
    "#pattern" : r"https://images\.mangafreak\.me/mangas/onepunch_man/onepunch_man_1/onepunch_man_1_\d+\.jpg",
    "#count"   : 24,

    "chapter"      : 1,
    "chapter_minor": "",
    "chapter_string": "1",
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Onepunch Man",
    "manga_slug"   : "Onepunch_Man",
},

{
    "#url"     : "https://ww2.mangafreak.me/Read1_Onepunch_Man_167e",
    "#class"   : mangafreak.MangafreakChapterExtractor,

    "chapter"      : 167,
    "chapter_minor": "e",
    "chapter_string": "167e",
},

{
    "#url"     : "https://ww2.mangafreak.me/Manga/Onepunch_Man",
    "#class"   : mangafreak.MangafreakMangaExtractor,
    "#pattern" : mangafreak.MangafreakChapterExtractor.pattern,
    "#count"   : range(150, 250),

    "lang"       : "en",
    "language"   : "English",
    "manga"      : "Onepunch-Man",
    "manga_slug" : "Onepunch_Man",
    "chapter"    : int,
},

)
