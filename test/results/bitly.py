# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import urlshortener


__tests__ = (
{
    "#url"     : "https://bit.ly/3cWIUgq",
    "#category": ("urlshortener", "bitly", "link"),
    "#class"   : urlshortener.UrlshortenerLinkExtractor,
    "#pattern" : "^https://gumroad.com/l/storm_b1",
    "#count"   : 1,
},

)
