# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nudostarforum


__tests__ = (
{
    "#url"     : "https://nudostar.com/forum/threads/aspen-rae.106714/",
    "#category": ("", "nudostarforum", "thread"),
    "#class"   : nudostarforum.NudostarforumThreadExtractor,
},

{
    "#url"     : "https://nudostar.com/forum/threads/aspen-rae.106714/page-2",
    "#category": ("", "nudostarforum", "thread"),
    "#class"   : nudostarforum.NudostarforumThreadExtractor,
},

{
    "#url"     : "https://nudostar.com/forum/threads/name.12345/post-67890",
    "#category": ("", "nudostarforum", "post"),
    "#class"   : nudostarforum.NudostarforumPostExtractor,
},

)
