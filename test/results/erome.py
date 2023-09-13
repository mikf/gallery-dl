# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import erome


__tests__ = (
{
    "#url"     : "https://www.erome.com/a/NQgdlWvk",
    "#category": ("", "erome", "album"),
    "#class"   : erome.EromeAlbumExtractor,
    "#pattern" : r"https://v\d+\.erome\.com/\d+/NQgdlWvk/j7jlzmYB_480p\.mp4",
    "#count"   : 1,

    "album_id": "NQgdlWvk",
    "num"     : 1,
    "title"   : "porn",
    "user"    : "yYgWBZw8o8qsMzM",
},

{
    "#url"     : "https://www.erome.com/a/TdbZ4ogi",
    "#category": ("", "erome", "album"),
    "#class"   : erome.EromeAlbumExtractor,
    "#pattern" : r"https://s\d+\.erome\.com/\d+/TdbZ4ogi/\w+",
    "#count"   : 6,

    "album_id": "TdbZ4ogi",
    "num"     : int,
    "title"   : "82e78cfbb461ad87198f927fcb1fda9a1efac9ff.",
    "user"    : "yYgWBZw8o8qsMzM",
},

{
    "#url"     : "https://www.erome.com/yYgWBZw8o8qsMzM",
    "#category": ("", "erome", "user"),
    "#class"   : erome.EromeUserExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "https://www.erome.com/search?q=cute",
    "#category": ("", "erome", "search"),
    "#class"   : erome.EromeSearchExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

)
