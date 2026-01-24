# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangatown


__tests__ = (
{
    "#url"     : "https://www.mangatown.com/manga/kimetsu_no_yaiba/c001/",
    "#category": ("", "mangatown", "chapter"),
    "#class"   : mangatown.MangatownChapterExtractor,
    "#pattern" : r"https://zjcdn\.mangahere\.org/.*",
    "#count"   : ">= 20",
},

{
    "#url"     : "https://www.mangatown.com/manga/kimetsu_no_yaiba/c001/1.html",
    "#category": ("", "mangatown", "chapter"),
    "#class"   : mangatown.MangatownChapterExtractor,
    "#pattern" : r"https://zjcdn\.mangahere\.org/.*",
},

{
    "#url"     : "http://www.mangatown.com/manga/kimetsu_no_yaiba/c001/",
    "#category": ("", "mangatown", "chapter"),
    "#class"   : mangatown.MangatownChapterExtractor,
},

{
    "#url"     : "https://www.mangatown.com/manga/kimetsu_no_yaiba/",
    "#category": ("", "mangatown", "manga"),
    "#class"   : mangatown.MangatownMangaExtractor,
    "#pattern" : mangatown.MangatownChapterExtractor.pattern,
    "#count"   : ">= 100",
},

{
    "#url"     : "http://www.mangatown.com/manga/kimetsu_no_yaiba/",
    "#category": ("", "mangatown", "manga"),
    "#class"   : mangatown.MangatownMangaExtractor,
},

)
