# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.wikiversity.org/wiki/Title",
    "#category": ("wikimedia", "wikiversity", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://en.wikiversity.org/wiki/Category:Title",
    "#category": ("wikimedia", "wikiversity", "category"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
