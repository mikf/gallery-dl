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

    "content": r"""re:Gear up for #PokemonSwordShieldEX with special Mystery Gifts! 

You’ll be able to receive four Galarian form Pokémon with Hidden Abilities, plus some very useful items. It’s our \(Mystery\) Gift to you, Trainers! 

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

)
