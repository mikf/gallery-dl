# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import misskey


__tests__ = (
{
    "#url"     : "https://misskey.io/@lithla",
    "#category": ("misskey", "misskey.io", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
    "#pattern" : r"https://s\d+\.arkjp\.net/misskey/[\w-]+\.\w+",
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://misskey.io/@blooddj@pawoo.net",
    "#category": ("misskey", "misskey.io", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://misskey.io/@blooddj@pawoo.net/following",
    "#category": ("misskey", "misskey.io", "following"),
    "#class"   : misskey.MisskeyFollowingExtractor,
    "#count"    : ">= 6",
    "#extractor": False,
},

{
    "#url"     : "https://misskey.io/notes/9bhqfo835v",
    "#category": ("misskey", "misskey.io", "note"),
    "#class"   : misskey.MisskeyNoteExtractor,
    "#pattern" : r"https://s\d+\.arkjp\.net/misskey/[\w-]+\.\w+",
    "#count"   : 4,
},

{
    "#url"     : "https://misskey.io/notes/9brq7z1re6",
    "#category": ("misskey", "misskey.io", "note"),
    "#class"   : misskey.MisskeyNoteExtractor,
},

{
    "#url"     : "https://misskey.io/my/favorites",
    "#category": ("misskey", "misskey.io", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

{
    "#url"     : "https://misskey.io/api/i/favorites",
    "#category": ("misskey", "misskey.io", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

)
