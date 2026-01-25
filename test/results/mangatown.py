# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangatown


__tests__ = (
{
    "#url"     : "https://www.mangatown.com/manga/kimetsu_no_yaiba/c001/",
    "#class"   : mangatown.MangatownChapterExtractor,
    "#pattern" : r"https://zjcdn\.mangahere\.org/.*",
    "#count"   : ">= 20",

    "chapter"      : 1,
    "chapter_id"   : 368511,
    "chapter_minor": "",
    "count"        : 55,
    "page"         : range(1, 55),
    "extension"    : "jpg",
    "filename"     : str,
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Kimetsu no Yaiba",
    "manga_id"     : 21437,
    "volume"       : 0,

},

{
    "#url"     : "https://www.mangatown.com/manga/kimetsu_no_yaiba/c001/1.html",
    "#class"   : mangatown.MangatownChapterExtractor,
    "#pattern" : r"https://zjcdn\.mangahere\.org/.*",
},

{
    "#url"     : "http://www.mangatown.com/manga/kimetsu_no_yaiba/c001/",
    "#class"   : mangatown.MangatownChapterExtractor,
},

{
    "#url"     : "https://www.mangatown.com/manga/kimetsu_no_yaiba/",
    "#class"   : mangatown.MangatownMangaExtractor,
    "#pattern" : mangatown.MangatownChapterExtractor.pattern,
    "#count"   : ">= 100",

    "chapter"  : int,
    "chapter_minor": {"", ".5", ".6"},
    "date"     : str,
    "lang"     : "en",
    "language" : "English",
    "manga"    : "Kimetsu no Yaiba",
    "title"    : str,

},

{
    "#url"     : "http://www.mangatown.com/manga/kimetsu_no_yaiba/",
    "#class"   : mangatown.MangatownMangaExtractor,
},

)
