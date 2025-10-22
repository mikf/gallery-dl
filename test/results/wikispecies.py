# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://species.wikimedia.org/wiki/Geranospiza",
    "#category": ("wikimedia", "wikispecies", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#results"     : "https://upload.wikimedia.org/wikipedia/commons/0/01/Geranospiza_caerulescens.jpg?format=original",
    "#sha1_content": "3a17c14b15489928e4154f826af1c42afb5a523e",
},

{
    "#url"     : "https://species.wikimedia.org/wiki/Category:Names",
    "#category": ("wikimedia", "wikispecies", "category"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
