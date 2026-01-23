# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter


__tests__ = (
{
    "#url"     : "https://lightbrd.com/supernaturepics/status/604341487988576256",
    "#category": ("nitter", "lightbrd", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
},

{
    "#url"     : "https://lightbrd.com/supernaturepics",
    "#category": ("nitter", "lightbrd", "tweets"),
    "#class"   : nitter.NitterTweetsExtractor,
},

)
