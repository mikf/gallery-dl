# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.mariowiki.com/Rabbit",
    "#category": ("wikimedia", "mariowiki", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#pattern" : r"https://mario\.wiki\.gallery/images/.+",
    "#count"   : range(20, 50),
},

)
