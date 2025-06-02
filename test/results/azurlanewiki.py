# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://azurlane.koumakan.jp/wiki/Azur_Lane_Wiki",
    "#category": ("wikimedia", "azurlanewiki", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://azurlane.koumakan.jp/wiki/Louisville/Gallery",
    "#comment" : "entries with missing 'imageinfo' (#5384)",
    "#category": ("wikimedia", "azurlanewiki", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#count"   : "> 10",
},

)
