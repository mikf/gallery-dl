# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter
import datetime


__tests__ = (
{
    "#url"     : "https://nitter.net/supernaturepics",
    "#category": ("nitter", "nitter.net", "tweets"),
    "#class"   : nitter.NitterTweetsExtractor,
    "#pattern" : r"https://nitter\.net/pic/orig/media%2F[\w-]+\.(jpg|png)$",
    "#range"   : "1-20",
    "#count"   : 20,

    "author"  : {
        "name": "supernaturepics",
        "nick": "Nature Pictures",
    },
    "comments": int,
    "content" : str,
    "count"   : 1,
    "date"    : datetime.datetime,
    "likes"   : int,
    "quotes"  : int,
    "retweets": int,
    "tweet_id": r"re:\d+",
    "user"    : {
        "date"            : "dt:2015-01-12 10:25:00",
        "description"     : "The very best nature pictures.",
        "favourites_count": int,
        "followers_count" : int,
        "friends_count"   : int,
        "id"              : "2976459548",
        "name"            : "supernaturepics",
        "nick"            : "Nature Pictures",
        "profile_banner"  : "https://nitter.net/pic/https%3A%2F%2Fpbs.twimg.com%2Fprofile_banners%2F2976459548%2F1421058583%2F1500x500",
        "profile_image"   : "https://nitter.net/pic/pbs.twimg.com%2Fprofile_images%2F554585280938659841%2FFLVAlX18.jpeg",
        "statuses_count"  : 1568,
        "verified"        : False,
    },
},

{
    "#url"     : "https://nitter.net/supernaturepics/with_replies",
    "#category": ("nitter", "nitter.net", "replies"),
    "#class"   : nitter.NitterRepliesExtractor,
    "#pattern" : r"https://nitter\.net/pic/orig/media%2F[\w-]+\.(jpg|png)$",
    "#range"   : "1-20",
},

{
    "#url"     : "https://nitter.net/supernaturepics/media",
    "#category": ("nitter", "nitter.net", "media"),
    "#class"   : nitter.NitterMediaExtractor,
    "#pattern" : r"https://nitter\.net/pic/orig/media%2F[\w-]+\.(jpg|png)$",
    "#range"   : "1-20",
},

{
    "#url"     : "https://nitter.net/supernaturepics/search",
    "#category": ("nitter", "nitter.net", "search"),
    "#class"   : nitter.NitterSearchExtractor,
    "#pattern" : r"https://nitter\.net/pic/orig/media%2F[\w-]+\.(jpg|png)$",
    "#range"   : "1-20",
},

{
    "#url"     : "https://nitter.net/supernaturepics/status/604341487988576256",
    "#category": ("nitter", "nitter.net", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#sha1_url"    : "3f2b64e175bf284aa672c3bb53ed275e470b919a",
    "#sha1_content": "ab05e1d8d21f8d43496df284d31e8b362cd3bcab",

    "comments" : int,
    "content"  : "Big Wedeene River, Canada",
    "count"    : 1,
    "date"     : "dt:2015-05-29 17:40:00",
    "extension": "jpg",
    "filename" : "CGMNYZvW0AIVoom",
    "likes"    : int,
    "num"      : 1,
    "quotes"   : int,
    "retweets" : int,
    "tweet_id" : "604341487988576256",
    "url"      : "https://nitter.net/pic/orig/media%2FCGMNYZvW0AIVoom.jpg",
    "user"     : {
        "name": "supernaturepics",
        "nick": "Nature Pictures",
    },
},

{
    "#url"     : "https://nitter.net/StobiesGalaxy/status/1270755918330896395",
    "#comment" : "'quoted' option (#854)",
    "#category": ("nitter", "nitter.net", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#options" : {"quoted": True},
    "#pattern" : r"https://nitter\.net/pic/orig/media%2FEa[KG].+\.jpg",
    "#count"   : 8,
},

)
