# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import misskey


__tests__ = (
{
    "#url"     : "https://misskey.art/@mamad0r",
    "#category": ("misskey", "misskey.art", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://misskey.art/@mamad0r/info",
        "https://misskey.art/@mamad0r/avatar",
        "https://misskey.art/@mamad0r/banner",
        "https://misskey.art/@mamad0r/notes",
    ),
},

{
    "#url"     : "https://misskey.art/@mamad0r/info",
    "#category": ("misskey", "misskey.art", "info"),
    "#class"   : misskey.MisskeyInfoExtractor,
},

{
    "#url"     : "https://misskey.art/@mamad0r/avatar",
    "#category": ("misskey", "misskey.art", "avatar"),
    "#class"   : misskey.MisskeyAvatarExtractor,
    "#results" : "https://files.misskey.art//583b26e0-97bb-439a-bce9-0ef27e00cd5d.jpg",
    "#sha1_content": "43a18e346cee05341da0cfa232c2754644473146",

    "id"       : "avatar",
    "file"     : {"id": "583b26e0-97bb-439a-bce9-0ef27e00cd5d"},
    "user"     : {"id": "9d5fgmcxm1"},
},

{
    "#url"     : "https://misskey.art/@risiy/banner",
    "#category": ("misskey", "misskey.art", "background"),
    "#class"   : misskey.MisskeyBackgroundExtractor,
    "#results" : "https://files.misskey.art/f02b97ea-dc2a-4b5a-acf1-dfe360ba8bd8.png",
},

{
    "#url"     : "https://misskey.art/@mamad0r/notes",
    "#category": ("misskey", "misskey.art", "notes"),
    "#class"   : misskey.MisskeyNotesExtractor,
    "#pattern" : r"https://files\.misskey\.art/(webpublic-)?[\w-]{36}\.\w+",
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://misskey.art/@mamad0r/following",
    "#category": ("misskey", "misskey.art", "following"),
    "#class"   : misskey.MisskeyFollowingExtractor,
    "#pattern" : misskey.MisskeyUserExtractor.pattern,
    "#results" : (
        "https://misskey.art/@tukushiA@misskey.io",
        "https://misskey.art/@mamad0r@misskey.io",
        "https://misskey.art/@shuumai@misskey.io",
    ),
},

{
    "#url"     : "https://misskey.art/notes/aaqoo4hsi6",
    "#category": ("misskey", "misskey.art", "note"),
    "#class"   : misskey.MisskeyNoteExtractor,
    "#results" : "https://files.misskey.art/15694b3d-d157-4af5-84bc-5ff088ab3e8b.jpg",
},

{
    "#url"     : "https://misskey.art/my/favorites",
    "#category": ("misskey", "misskey.art", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

{
    "#url"     : "https://misskey.art/api/i/favorites",
    "#category": ("misskey", "misskey.art", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

)
