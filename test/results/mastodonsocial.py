# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mastodon


__tests__ = (
{
    "#url"     : "https://mastodon.social/@jk",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
    "#pattern" : r"https://files.mastodon.social/media_attachments/files/(\d+/){3,}original/\w+",
    "#range"   : "1-60",
    "#count"   : 60,
},

{
    "#url"     : "https://mastodon.social/@ponapalt@ukadon.shillest.net",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
    "#pattern" : r"https://files\.mastodon\.social/cache/media_attachments/files/.+/original/\w{16}\.\w+$",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://mastodon.social/@gallerydl",
    "#comment" : "reblogged/'boosted' posts (#4580)",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
    "#options" : {"reblogs": True},
    "#archive" : False,
    "#urls": (
        "https://files.mastodon.social/media_attachments/files/111/330/852/486/713/967/original/2c25ade55a9d1af2.jpg",
        "https://files.mastodon.social/media_attachments/files/111/331/603/082/304/823/original/e12cde371c88c1b0.png",
        "https://files.mastodon.social/media_attachments/files/111/331/603/082/304/823/original/e12cde371c88c1b0.png",
    ),
},

{
    "#url"     : "https://mastodon.social/@id:10843",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.social/users/id:10843",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.social/users/jk",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.social/users/yoru_nine@pawoo.net",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.social/web/@jk",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.social/bookmarks",
    "#category": ("mastodon", "mastodon.social", "bookmark"),
    "#class"   : mastodon.MastodonBookmarkExtractor,
},

{
    "#url"     : "https://mastodon.social/@gallerydl/following",
    "#category": ("mastodon", "mastodon.social", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
    "#extractor": False,
    "#urls"     : (
        "https://mastodon.ie/@RustyBertrand",
        "https://ravenation.club/@soundwarrior20",
        "https://mastodon.social/@0x4f",
        "https://mastodon.social/@christianselig",
        "https://saturation.social/@clive",
        "https://mastodon.social/@sjvn",
    ),

    "acct"          : str,
    "avatar"        : r"re:https://files.mastodon.social/.+\.\w+$",
    "avatar_static" : r"re:https://files.mastodon.social/.+\.\w+$",
    "bot"           : False,
    "created_at"    : r"re:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z",
    "discoverable"  : True,
    "display_name"  : str,
    "emojis"        : [],
    "fields"        : list,
    "followers_count": int,
    "following_count": int,
    "group"         : False,
    "header"        : str,
    "header_static" : str,
    "id"            : r"re:\d+",
    "last_status_at": r"re:\d{4}-\d{2}-\d{2}",
    "locked"        : bool,
    "note"          : str,
    "statuses_count": int,
    "uri"           : str,
    "url"           : str,
    "username"      : str,

},

{
    "#url"     : "https://mastodon.social/@0x4f/following",
    "#category": ("mastodon", "mastodon.social", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://mastodon.social/users/id:10843/following",
    "#category": ("mastodon", "mastodon.social", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://mastodon.social/@jk/103794036899778366",
    "#category": ("mastodon", "mastodon.social", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#count"   : 4,

    "count": 4,
    "num"  : int,
},

)
