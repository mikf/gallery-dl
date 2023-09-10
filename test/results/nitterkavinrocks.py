# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter


__tests__ = (
{
    "#url"     : "https://nitter.kavin.rocks/id:2976459548",
    "#category": ("nitter", "nitter.kavin.rocks", "tweets"),
    "#class"   : nitter.NitterTweetsExtractor,
},

{
    "#url"     : "https://nitter.kavin.rocks/id:2976459548/with_replies",
    "#category": ("nitter", "nitter.kavin.rocks", "replies"),
    "#class"   : nitter.NitterRepliesExtractor,
},

{
    "#url"     : "https://nitter.kavin.rocks/id:2976459548/media",
    "#category": ("nitter", "nitter.kavin.rocks", "media"),
    "#class"   : nitter.NitterMediaExtractor,
    "#pattern" : r"https://nitter\.kavin\.rocks/pic/orig/media%2F[\w-]+\.(jpg|png)$",
    "#range"   : "1-20",
},

{
    "#url"     : "https://nitter.kavin.rocks/id:2976459548/search",
    "#category": ("nitter", "nitter.kavin.rocks", "search"),
    "#class"   : nitter.NitterSearchExtractor,
},

{
    "#url"     : "https://nitter.kavin.rocks/ed1conf/status/1163841619336007680",
    "#comment" : "Nitter tweet (#890)",
    "#category": ("nitter", "nitter.kavin.rocks", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#sha1_url"    : "e115bd1c86c660064e392b05269bbcafcd8c8b7a",
    "#sha1_content": "f29501e44d88437fe460f5c927b7543fda0f6e34",
},

)
