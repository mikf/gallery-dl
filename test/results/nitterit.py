# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter


__tests__ = (
{
    "#url"     : "https://nitter.it/POTUS/status/1639409307878928384",
    "#category": ("nitter", "nitter.it", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#count"   : 0,
},

)
