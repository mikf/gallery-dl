# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://bulbapedia.bulbagarden.net/wiki/Jet",
    "#category": ("wikimedia", "bulbapedia", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#pattern" : r"https://archives\.bulbagarden\.net/media/upload/\w+/\w+/[^/?#]+",
    "#count"   : range(8, 30),
},

{
    "#url"     : "https://archives.bulbagarden.net/wiki/File:0460Abomasnow-Mega.png",
    "#category": ("wikimedia", "bulbapedia", "file"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#pattern" : r"https://archives\.bulbagarden\.net/media/upload/\w+/\w+/[^/?#]+",
    "#count"   : range(8, 12),
    "#archive" : False,
},

)
