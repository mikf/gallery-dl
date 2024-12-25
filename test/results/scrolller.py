# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import scrolller


__tests__ = (
{
    "#url"    : "https://scrolller.com/r/AmateurPhotography",
    "#class"  : scrolller.ScrolllerSubredditExtractor,
    "#pattern": r"https://\w+\.scrolller\.com/(\w+/)?[\w-]+-\w+\.(jpg|png)",
    "#range"  : "1-100",
    "#count"  : 100,

    "albumUrl"        : None,
    "displayName"     : None,
    "fullLengthSource": None,
    "gfycatSource"    : None,
    "hasAudio"        : None,
    "height"          : int,
    "id"              : int,
    "isFavorite"      : False,
    "isNsfw"          : False,
    "isOptimized"     : bool,
    "isPaid"          : None,
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
    "username"        : None,
    "width"           : int,
},

{
    "#url"  : "https://scrolller.com/cabin-in-northern-finland-7nagf1929p",
    "#class": scrolller.ScrolllerPostExtractor,
    "#urls" : "https://yocto.scrolller.com/cabin-in-northern-finland-93vjsuxmcz.jpg",

    "albumUrl"        : None,
    "displayName"     : None,
    "extension"       : "jpg",
    "filename"        : "cabin-in-northern-finland-93vjsuxmcz",
    "fullLengthSource": None,
    "gfycatSource"    : None,
    "hasAudio"        : None,
    "height"          : 1350,
    "id"              : 10478722,
    "isNsfw"          : False,
    "isOptimized"     : False,
    "isPaid"          : None,
    "mediaSources"    : list,
    "ownerAvatar"     : None,
    "redditPath"      : "/r/AmateurPhotography/comments/jj048q/cabin_in_northern_finland/",
    "redgifsSource"   : None,
    "subredditId"     : 0,
    "subredditTitle"  : "AmateurPhotography",
    "subredditUrl"    : "/r/AmateurPhotography",
    "tags"            : None,
    "title"           : "Cabin in northern Finland",
    "url"             : "https://yocto.scrolller.com/cabin-in-northern-finland-93vjsuxmcz.jpg",
    "username"        : None,
    "width"           : 1080,
},

{
    "#url"    : "https://scrolller.com/following",
    "#class"  : scrolller.ScrolllerFollowingExtractor,
    "#pattern": scrolller.ScrolllerSubredditExtractor.pattern,
    "#auth"   : True,
},

)
