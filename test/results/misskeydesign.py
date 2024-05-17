# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import misskey


__tests__ = (
{
    "#url"     : "https://misskey.design/@machina_3D",
    "#category": ("misskey", "misskey.design", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
    "#pattern" : r"https://file\.misskey\.design/post/[\w-]{36}\.\w+",
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://misskey.design/@blooddj@pawoo.net",
    "#category": ("misskey", "misskey.design", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
    "#count"   : "> 30",
},

{
    "#url"     : "https://misskey.design/@kujyo_t/following",
    "#category": ("misskey", "misskey.design", "following"),
    "#class"   : misskey.MisskeyFollowingExtractor,
    "#count"    : ">= 250",
},

{
    "#url"     : "https://misskey.design/notes/9jva1danjc",
    "#category": ("misskey", "misskey.design", "note"),
    "#class"   : misskey.MisskeyNoteExtractor,
    "#urls"    : "https://file.misskey.design/post/a8d27901-24e1-42ab-b8a6-1e09c98c6f55.webp",
},

{
    "#url"     : "https://misskey.design/my/favorites",
    "#category": ("misskey", "misskey.design", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

{
    "#url"     : "https://misskey.design/api/i/favorites",
    "#category": ("misskey", "misskey.design", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

)
