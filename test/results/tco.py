# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import urlshortener
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://t.co/bCgBY8Iv5n",
    "#category": ("urlshortener", "tco", "link"),
    "#class"   : urlshortener.UrlshortenerLinkExtractor,
    "#pattern" : "^https://twitter.com/elonmusk/status/1421395561324896257/photo/1",
    "#count"   : 1,
},

{
    "#url"     : "https://t.co/abcdefghij",
    "#category": ("urlshortener", "tco", "link"),
    "#class"   : urlshortener.UrlshortenerLinkExtractor,
    "#exception": exception.NotFoundError,
},

)
