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
    "#url"     : "https://mastodon.social/@yoru_nine@pawoo.net",
    "#category": ("mastodon", "mastodon.social", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
    "#pattern" : r"https://mastodon\.social/media_proxy/\d+/original",
    "#range"   : "1-10",
    "#count"   : 10,
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
    "#url"     : "https://mastodon.social/users/0x4f/following",
    "#category": ("mastodon", "mastodon.social", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
    "#count"    : ">= 20",
    "#extractor": False,
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
