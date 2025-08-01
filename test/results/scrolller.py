# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import scrolller


__tests__ = (
{
    "#url"    : "https://scrolller.com/r/AmateurPhotography",
    "#class"  : scrolller.ScrolllerSubredditExtractor,
    "#pattern": r"https://images\.scrolller\.com/\w+/[\w-]+\.\w+",
    "#range"  : "1-100",
    "#count"  : 100,

    "displayName"     : None,
    "fullLengthSource": None,
    "gfycatSource"    : None,
    "hasAudio"        : bool,
    "height"          : int,
    "id"              : int,
    "isFavorite"      : False,
    "isNsfw"          : False,
    "isOptimized"     : bool,
    "isPaid"          : bool,
    "mediaSources"    : list,
    "ownerAvatar"     : None,
    "redditPath"      : r"re:/r/AmateurPhotography/comments/...",
    "redgifsSource"   : None,
    "subredditId"     : {0, 413},
    "subredditTitle"  : "AmateurPhotography",
    "subredditUrl"    : "/r/AmateurPhotography",
    "tags"            : None,
    "title"           : str,
    "url"             : str,
    "username"        : str,
    "width"           : int,
},

{
    "#url"    : "https://scrolller.com/r/gonewanton",
    "#comment": "NSFW subreddit",
    "#class"  : scrolller.ScrolllerSubredditExtractor,
    "#pattern": r"https://\w+\.scrolller\.com/(\w+/)?[\w-]+\.\w+",
    "#range"  : "1-100",
    "#count"  : 100,

    "isNsfw"          : True,
    "redditPath"      : r"re:/r/gonewanton/comments/...",
    "subredditId"     : {0, 4403},
    "subredditTitle"  : "gonewanton",
    "subredditUrl"    : "/r/gonewanton",
},

{
    "#url"  : "https://scrolller.com/cabin-in-northern-finland-7nagf1929p",
    "#class": scrolller.ScrolllerPostExtractor,
    "#pattern": "https://images.scrolller.com/yocto/cabin-in-northern-finland-93vjsuxmcz.jpg",

    "count"           : 1,
    "displayName"     : None,
    "extension"       : "jpg",
    "filename"        : "cabin-in-northern-finland-93vjsuxmcz",
    "fullLengthSource": None,
    "gfycatSource"    : None,
    "hasAudio"        : False,
    "height"          : 1350,
    "id"              : 10478722,
    "isNsfw"          : False,
    "isOptimized"     : False,
    "isPaid"          : False,
    "mediaSources"    : list,
    "num"             : 0,
    "ownerAvatar"     : None,
    "redditPath"      : "/r/AmateurPhotography/comments/jj048q/cabin_in_northern_finland/",
    "redgifsSource"   : None,
    "subredditId"     : 413,
    "subredditTitle"  : "AmateurPhotography",
    "subredditUrl"    : "/r/AmateurPhotography",
    "tags"            : None,
    "title"           : "Cabin in northern Finland",
    "url"             : "https://images.scrolller.com/yocto/cabin-in-northern-finland-93vjsuxmcz.jpg",
    "username"        : "",
    "width"           : 1080,
},

{
    "#url"    : "https://scrolller.com/long-comic-the-twelve-tasks-of-eve-12ch1ve8ko",
    "#comment": "album post (#7339)",
    "#class"  : scrolller.ScrolllerPostExtractor,
    "#pattern": r"https://images\.scrolller\.com/\w+/long-comic-the-twelve-tasks-of-eve-\d+-\w+\.png",
    "#count"  : 177,

    "count": 177,
    "num"  : range(1, 177),
},

{
    "#url"    : "https://scrolller.com/some-quick-news-tboi-rule-34-mod-czedll1bum",
    "#comment": "album post with empty 'mediaSources' (#7428)",
    "#class"  : scrolller.ScrolllerPostExtractor,
    "#results": "https://images.scrolller.com/gamma/some-quick-news-tboi-rule-34-mod-1-50uolks94u.png",
    "#count"  : 1,

    "count": 1,
    "num"  : 1,
},

{
    "#url"    : "https://scrolller.com/following",
    "#class"  : scrolller.ScrolllerFollowingExtractor,
    "#pattern": scrolller.ScrolllerSubredditExtractor.pattern,
    "#auth"   : True,
},

)
