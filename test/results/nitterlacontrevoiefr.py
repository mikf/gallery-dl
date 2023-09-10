# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter


__tests__ = (
{
    "#url"     : "https://nitter.lacontrevoie.fr/supernaturepics",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "tweets"),
    "#class"   : nitter.NitterTweetsExtractor,
    "#pattern" : r"https://nitter\.lacontrevoie\.fr/pic/orig/media%2FCGMNYZvW0AIVoom\.jpg",
    "#range"   : "1",
    "#sha1_url": "54f4b55f2099dcc248f3fb7bfacf1349e08d8e2d",
},

{
    "#url"     : "https://nitter.lacontrevoie.fr/supernaturepics/with_replies",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "replies"),
    "#class"   : nitter.NitterRepliesExtractor,
},

{
    "#url"     : "https://nitter.lacontrevoie.fr/supernaturepics/media",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "media"),
    "#class"   : nitter.NitterMediaExtractor,
},

{
    "#url"     : "https://nitter.lacontrevoie.fr/supernaturepics/search",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "search"),
    "#class"   : nitter.NitterSearchExtractor,
},

{
    "#url"     : "https://nitter.lacontrevoie.fr/i/status/894001459754180609",
    "#comment" : "4 images",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#sha1_url": "9c51b3a4a1114535eb9b168bba97ad95db0d59ff",
},

{
    "#url"     : "https://nitter.lacontrevoie.fr/i/status/1065692031626829824",
    "#comment" : "video",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#pattern" : r"ytdl:https://nitter\.lacontrevoie\.fr/video/[0-9A-F]{10,}/https%3A%2F%2Fvideo.twimg.com%2Fext_tw_video%2F1065691868439007232%2Fpu%2Fpl%2Fnv8hUQC1R0SjhzcZ.m3u8%3Ftag%3D5",

    "extension": "mp4",
    "filename" : "nv8hUQC1R0SjhzcZ",
},

{
    "#url"     : "https://nitter.lacontrevoie.fr/i/status/1460044411165888515",
    "#comment" : "deleted quote tweet (#2225)",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://nitter.lacontrevoie.fr/i/status/1486373748911575046",
    "#comment" : "'Misleading' content",
    "#category": ("nitter", "nitter.lacontrevoie.fr", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#count"   : 4,
},

)
