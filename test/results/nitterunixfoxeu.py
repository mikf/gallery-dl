# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter


__tests__ = (
{
    "#url"     : "https://nitter.unixfox.eu/supernaturepics",
    "#category": ("nitter", "nitter.unixfox.eu", "tweets"),
    "#class"   : nitter.NitterTweetsExtractor,
},

{
    "#url"     : "https://nitter.unixfox.eu/i/user/2976459548/with_replies",
    "#category": ("nitter", "nitter.unixfox.eu", "replies"),
    "#class"   : nitter.NitterRepliesExtractor,
},

{
    "#url"     : "https://nitter.unixfox.eu/i/user/2976459548/media",
    "#category": ("nitter", "nitter.unixfox.eu", "media"),
    "#class"   : nitter.NitterMediaExtractor,
},

{
    "#url"     : "https://nitter.unixfox.eu/i/user/2976459548/search",
    "#category": ("nitter", "nitter.unixfox.eu", "search"),
    "#class"   : nitter.NitterSearchExtractor,
},

{
    "#url"     : "https://nitter.unixfox.eu/i/web/status/1170041925560258560",
    "#comment" : "Reply to deleted tweet (#403, #838)",
    "#category": ("nitter", "nitter.unixfox.eu", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#pattern" : r"https://nitter\.unixfox\.eu/pic/orig/media%2FEDzS7VrU0AAFL4_\.jpg",
},

{
    "#url"     : "https://nitter.unixfox.eu/mightbecurse/status/1492954264909479936",
    "#comment" : "age-restricted (#2354)",
    "#category": ("nitter", "nitter.unixfox.eu", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#count"   : 1,

    "date": "dt:2022-02-13 20:10:00",
},

)
