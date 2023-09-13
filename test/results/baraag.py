# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mastodon


__tests__ = (
{
    "#url"     : "https://baraag.net/@pumpkinnsfw",
    "#category": ("mastodon", "baraag", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://baraag.net/bookmarks",
    "#category": ("mastodon", "baraag", "bookmark"),
    "#class"   : mastodon.MastodonBookmarkExtractor,
},

{
    "#url"     : "https://baraag.net/users/pumpkinnsfw/following",
    "#category": ("mastodon", "baraag", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://baraag.net/@pumpkinnsfw/104364170556898443",
    "#category": ("mastodon", "baraag", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#sha1_content": "67748c1b828c58ad60d0fe5729b59fb29c872244",
},

)
