# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nitter


__tests__ = (
{
    "#url"     : "https://nitter.1d4.us/supernaturepics",
    "#category": ("nitter", "nitter.1d4.us", "tweets"),
    "#class"   : nitter.NitterTweetsExtractor,
    "#range"   : "1",

    "user": {"id": "2976459548"},
},

{
    "#url"     : "https://nitter.1d4.us/supernaturepics/with_replies",
    "#category": ("nitter", "nitter.1d4.us", "replies"),
    "#class"   : nitter.NitterRepliesExtractor,
},

{
    "#url"     : "https://nitter.1d4.us/supernaturepics/media",
    "#category": ("nitter", "nitter.1d4.us", "media"),
    "#class"   : nitter.NitterMediaExtractor,
},

{
    "#url"     : "https://nitter.1d4.us/supernaturepics/search",
    "#category": ("nitter", "nitter.1d4.us", "search"),
    "#class"   : nitter.NitterSearchExtractor,
},

{
    "#url"     : "https://nitter.1d4.us/playpokemon/status/1263832915173048321",
    "#comment" : "content with emoji, newlines, hashtags (#338)",
    "#category": ("nitter", "nitter.1d4.us", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,

    "content": r"""re:Gear up for #PokemonSwordShieldEX with special Mystery Gifts! \n
You’ll be able to receive four Galarian form Pokémon with Hidden Abilities, plus some very useful items. It’s our \(Mystery\) Gift to you, Trainers! \n
❓🎁➡️ """,
},

{
    "#url"     : "https://nitter.1d4.us/StobiesGalaxy/status/1270755918330896395",
    "#comment" : "quoted tweet (#526, #854)",
    "#category": ("nitter", "nitter.1d4.us", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#pattern" : r"https://nitter\.1d4\.us/pic/orig/enc/bWVkaWEvRWFL\w+LmpwZw==",
    "#count"   : 4,

    "filename": r"re:EaK.{12}",
},

{
    "#url"     : "https://nitter.1d4.us/i/status/894001459754180609",
    "#comment" : "4 images",
    "#category": ("nitter", "nitter.1d4.us", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#sha1_url": "bc6a91792ff6ec3ab9046f4f27299cc0e7ca7ce3",
},

{
    "#url"     : "https://nitter.1d4.us/i/status/1065692031626829824",
    "#comment" : "video",
    "#category": ("nitter", "nitter.1d4.us", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#pattern" : r"ytdl:https://nitter\.1d4\.us/video/enc/F00083CDE8D74/aHR0cHM6Ly92aWRlby50d2ltZy5jb20vZXh0X3R3X3ZpZGVvLzEwNjU2OTE4Njg0MzkwMDcyMzIvcHUvcGwvbnY4aFVRQzFSMFNqaHpjWi5tM3U4P3RhZz01",

    "extension": "mp4",
    "filename" : "nv8hUQC1R0SjhzcZ",
},

{
    "#url"     : "https://nitter.1d4.us/i/status/1460044411165888515",
    "#comment" : "deleted quote tweet (#2225)",
    "#category": ("nitter", "nitter.1d4.us", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://nitter.1d4.us/i/status/1486373748911575046",
    "#comment" : "'Misleading' content",
    "#category": ("nitter", "nitter.1d4.us", "tweet"),
    "#class"   : nitter.NitterTweetExtractor,
    "#count"   : 4,
},

)
