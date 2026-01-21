# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter


__tests__ = (
{
    "#url"     : "https://nitter.net/supernaturepics/status/604341487988576256",
    "#category": ("nitter", "nitter.net", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#results" : "https://nitter.net/pic/orig/media%2FCGMNYZvW0AIVoom.jpg",

    "comments" : 18,
    "content"  : "Big Wedeene River, Canada",
    "count"    : 1,
    "date"     : "dt:2015-05-29 17:40:00",
    "extension": "jpg",
    "filename" : "CGMNYZvW0AIVoom",
    "likes"    : 513,
    "num"      : 1,
    "quoted"   : False,
    "quotes"   : 0,
    "retweet"  : False,
    "retweets" : 455,
    "tweet_id" : "604341487988576256",
    "url"      : "https://nitter.net/pic/orig/media%2FCGMNYZvW0AIVoom.jpg",
    "author"   : {
        "name": "supernaturepics",
        "nick": "Nature Pictures",
    },
    "user"     : {
        "name": "supernaturepics",
        "nick": "Nature Pictures",
    },
},

{
    "#url"     : "https://nitter.net/supernaturepics",
    "#category": ("nitter", "nitter.net", "tweets"),
    "#class"   : nitter.NitterTweetsExtractor,
},

)
