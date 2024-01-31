# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.wiktionary.org/wiki/Word",
    "#category": ("wikimedia", "wiktionary", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://en.wiktionary.org/wiki/Category:Words",
    "#category": ("wikimedia", "wiktionary", "category"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
