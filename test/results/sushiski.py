# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import misskey


__tests__ = (
{
    "#url"     : "https://sushi.ski/@ui@misskey.04.si",
    "#category": ("misskey", "sushi.ski", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
},

{
    "#url"     : "https://sushi.ski/@hatusimo_sigure/following",
    "#category": ("misskey", "sushi.ski", "following"),
    "#class"   : misskey.MisskeyFollowingExtractor,
},

{
    "#url"     : "https://sushi.ski/notes/9bm3x4ksqw",
    "#category": ("misskey", "sushi.ski", "note"),
    "#class"   : misskey.MisskeyNoteExtractor,
    "#pattern" : r"https://media\.sushi\.ski/files/[\w-]+\.png",
    "#count"   : 1,
},

{
    "#url"     : "https://sushi.ski/my/favorites",
    "#category": ("misskey", "sushi.ski", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

)
