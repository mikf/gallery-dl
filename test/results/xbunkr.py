# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lolisafe


__tests__ = (
{
    "#url"     : "https://xbunkr.com/a/TA0bu3F4",
    "#category": ("lolisafe", "xbunkr", "album"),
    "#class"   : lolisafe.LolisafeAlbumExtractor,
    "#pattern" : r"https://media\.xbunkr\.com/[^.]+\.\w+",
    "#count"   : 861,

    "album_id"  : "TA0bu3F4",
    "album_name": "Hannahowo Onlyfans Photos",
},

{
    "#url"     : "https://xbunkr.com/a/GNQc2I5d",
    "#category": ("lolisafe", "xbunkr", "album"),
    "#class"   : lolisafe.LolisafeAlbumExtractor,
},

)
