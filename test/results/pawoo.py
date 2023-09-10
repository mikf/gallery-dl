# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mastodon


__tests__ = (
{
    "#url"     : "https://pawoo.net/@yoru_nine/",
    "#category": ("mastodon", "pawoo", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
    "#range"   : "1-60",
    "#count"   : 60,
},

{
    "#url"     : "https://pawoo.net/bookmarks",
    "#category": ("mastodon", "pawoo", "bookmark"),
    "#class"   : mastodon.MastodonBookmarkExtractor,
},

{
    "#url"     : "https://pawoo.net/users/yoru_nine/following",
    "#category": ("mastodon", "pawoo", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://pawoo.net/@yoru_nine/105038878897832922",
    "#category": ("mastodon", "pawoo", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#sha1_content": "b52e807f8ab548d6f896b09218ece01eba83987a",
},

)
