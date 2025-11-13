# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangafox


__tests__ = (
{
    "#url"     : "http://fanfox.net/manga/kidou_keisatsu_patlabor/v05/c006.2/1.html",
    "#category": ("", "mangafox", "chapter"),
    "#class"   : mangafox.MangafoxChapterExtractor,
    "#sha1_metadata": "5661dab258d42d09d98f194f7172fb9851a49766",
    "#sha1_content" : "5c50c252dcf12ffecf68801f4db8a2167265f66c",
},

{
    "#url"     : "http://mangafox.me/manga/kidou_keisatsu_patlabor/v05/c006.2/",
    "#category": ("", "mangafox", "chapter"),
    "#class"   : mangafox.MangafoxChapterExtractor,
},

{
    "#url"     : "http://fanfox.net/manga/black_clover/vTBD/c295/1.html",
    "#category": ("", "mangafox", "chapter"),
    "#class"   : mangafox.MangafoxChapterExtractor,
},

{
    "#url"     : "https://fanfox.net/manga/kanojo_mo_kanojo",
    "#category": ("", "mangafox", "manga"),
    "#class"   : mangafox.MangafoxMangaExtractor,
    "#pattern" : mangafox.MangafoxChapterExtractor.pattern,
    "#count"   : ">=60",

    "author"        : "HIROYUKI",
    "chapter"       : int,
    "chapter_minor" : r"re:^(\.\d+)?$",
    "chapter_string": r"re:(v\d+/)?c\d+",
    "date"          : "type:datetime",
    "description"   : "High school boy Naoya gets a confession from Momi, a cute and friendly girl. However, Naoya already has a girlfriend, Seki... but Momi is too good a catch to let go. Momi and Nagoya's goal becomes clear: convince Seki to accept being an item with the two of them. Will she budge?",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "Kanojo mo Kanojo",
    "tags"          : [
        "Comedy",
        "Romance",
        "School Life",
        "Shounen",
    ],
    "volume"        : int,
},

{
    "#url"     : "https://mangafox.me/manga/shangri_la_frontier",
    "#category": ("", "mangafox", "manga"),
    "#class"   : mangafox.MangafoxMangaExtractor,
    "#pattern" : mangafox.MangafoxChapterExtractor.pattern,
    "#count"   : ">=45",
},

{
    "#url"     : "https://m.fanfox.net/manga/sentai_daishikkaku",
    "#category": ("", "mangafox", "manga"),
    "#class"   : mangafox.MangafoxMangaExtractor,
},

)
