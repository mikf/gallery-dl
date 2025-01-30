# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import redgifs


__tests__ = (
{
    "#url"     : "https://www.redgifs.com/users/mmj",
    "#category": ("", "redgifs", "user"),
    "#class"   : redgifs.RedgifsUserExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[\w-]+\.mp4",
    "#count"   : range(40, 60),
},

{
    "#url"     : "https://www.redgifs.com/users/mmj?order=old",
    "#comment" : "'order' URL parameter (#4583)",
    "#category": ("", "redgifs", "user"),
    "#class"   : redgifs.RedgifsUserExtractor,
    "#range"   : "1-5",
    "#patterns": (
        r"https://thumbs\d+\.redgifs\.com/ShoddyOilyHarlequinbug\.mp4",
        r"https://thumbs\d+\.redgifs\.com/UnevenPrestigiousKilldeer\.mp4",
        r"https://thumbs\d+\.redgifs\.com/EveryShockingFlickertailsquirrel\.mp4",
        r"https://thumbs\d+\.redgifs\.com/NegativeWarlikeAmericancurl\.mp4",
        r"https://thumbs\d+\.redgifs\.com/PopularTerribleFritillarybutterfly\.mp4",
    ),
},

{
    "#url"     : "https://v3.redgifs.com/users/lamsinka89",
    "#comment" : "'v3' subdomain (#3588, #3589)",
    "#category": ("", "redgifs", "user"),
    "#class"   : redgifs.RedgifsUserExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[\w-]+\.(mp4|jpg)",
    "#count"   : ">= 100",
},

{
    "#url"     : "https://www.redgifs.com/users/boombah123/collections/2631326bbd",
    "#category": ("", "redgifs", "collection"),
    "#class"   : redgifs.RedgifsCollectionExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[\w-]+\.mp4",
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.redgifs.com/users/boombah123/collections/9e6f7dd41f",
    "#category": ("", "redgifs", "collection"),
    "#class"   : redgifs.RedgifsCollectionExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[\w-]+\.mp4",
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.redgifs.com/users/boombah123/collections",
    "#category": ("", "redgifs", "collections"),
    "#class"   : redgifs.RedgifsCollectionsExtractor,
    "#pattern" : r"https://www\.redgifs\.com/users/boombah123/collections/\w+",
    "#count"   : ">= 3",
},

{
    "#url"     : "https://www.redgifs.com/niches/just-boobs",
    "#category": ("", "redgifs", "niches"),
    "#class"   : redgifs.RedgifsNichesExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[\w-]+\.(mp4|jpg)",
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.redgifs.com/niches/thick-booty",
    "#category": ("", "redgifs", "niches"),
    "#class"   : redgifs.RedgifsNichesExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[\w-]+\.(mp4|jpg)",
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.redgifs.com/gifs/jav",
    "#category": ("", "redgifs", "search"),
    "#class"   : redgifs.RedgifsSearchExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[A-Za-z-]+\.(mp4|jpg)",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.redgifs.com/browse?tags=JAV",
    "#category": ("", "redgifs", "search"),
    "#class"   : redgifs.RedgifsSearchExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[A-Za-z-]+\.(mp4|jpg)",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.redgifs.com/gifs/jav?order=best&verified=1",
    "#category": ("", "redgifs", "search"),
    "#class"   : redgifs.RedgifsSearchExtractor,
},

{
    "#url"     : "https://www.redgifs.com/browse?type=i&verified=y&order=top7",
    "#category": ("", "redgifs", "search"),
    "#class"   : redgifs.RedgifsSearchExtractor,
},

{
    "#url"     : "https://v3.redgifs.com/browse?tags=JAV",
    "#category": ("", "redgifs", "search"),
    "#class"   : redgifs.RedgifsSearchExtractor,
},

{
    "#url"     : "https://redgifs.com/watch/foolishforkedabyssiniancat",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,
    "#pattern"     : r"https://\w+\.redgifs\.com/FoolishForkedAbyssiniancat\.mp4",
    "#sha1_content": "f6e03f1df9a2ff2a74092f53ee7580d2fb943533",
},

{
    "#url"     : "https://www.redgifs.com/watch/desertedbaregraywolf",
    "#comment" : "gallery (#4021)",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,
    "#pattern" : r"https://\w+\.redgifs\.com/[A-Za-z-]+\.jpg",
    "#count"   : 4,

    "num"    : int,
    "count"  : 4,
    "gallery": "187ad979693-1922-fc66-0000-a96fb07b8a5d",
},

{
    "#url"     : "https://redgifs.com/ifr/FoolishForkedAbyssiniancat",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,
},

{
    "#url"     : "https://i.redgifs.com/i/FoolishForkedAbyssiniancat",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,
},

{
    "#url"     : "https://www.gifdeliverynetwork.com/foolishforkedabyssiniancat",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,
},

{
    "#url"     : "https://v3.redgifs.com/watch/FoolishForkedAbyssiniancat",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,
},

{
    "#url"     : "https://v3.redgifs.com/watch/605025947780972895",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,

    "id": "humblegrippingmole",
},

{
    "#url"     : "https://www.gfycat.com/foolishforkedabyssiniancat",
    "#category": ("", "redgifs", "image"),
    "#class"   : redgifs.RedgifsImageExtractor,
},

)
