# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.wiki.gg/wiki/Title",
    "#comment" : "for scripts/supportedsites.py",
    "#category": ("wikimedia", "wikigg-www", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://hearthstone.wiki.gg/wiki/Flame_Juggler",
    "#category": ("wikimedia", "wikigg-hearthstone", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
