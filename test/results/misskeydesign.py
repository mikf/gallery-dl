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
    "#options" : {"include": "all"},
    "#results" : (
        "https://misskey.design/@machina_3D/info",
        "https://misskey.design/@machina_3D/avatar",
        "https://misskey.design/@machina_3D/banner",
        "https://misskey.design/@machina_3D/notes",
    ),
},

{
    "#url"     : "https://misskey.design/@machina_3D/notes",
    "#category": ("misskey", "misskey.design", "notes"),
    "#class"   : misskey.MisskeyNotesExtractor,
    "#pattern" : r"https://file\.misskey\.design/post/(webpublic-)?[\w-]{36}\.\w+",
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://misskey.design/@machina_3D/avatar",
    "#category": ("misskey", "misskey.design", "avatar"),
    "#class"   : misskey.MisskeyAvatarExtractor,
    "#results" : "https://file.misskey.design/post/f2cd76a4-e5e5-4c46-b45d-5cd28e0fdafe.png",
    "#sha1_content": "5ffa5b43513ed2e77f26ef9d49a91bb0d3e76847",

    "extension": "png",
    "filename" : "f2cd76a4-e5e5-4c46-b45d-5cd28e0fdafe",
    "id"       : "avatar",
    "instance" : "misskey.design",
    "file"     : {"id": "f2cd76a4-e5e5-4c46-b45d-5cd28e0fdafe"},
    "user"     : {"id": "9bxksu5vqi"},
},

{
    "#url"     : "https://misskey.design/@machina_3D/banner",
    "#category": ("misskey", "misskey.design", "background"),
    "#class"   : misskey.MisskeyBackgroundExtractor,
    "#results" : "https://file.misskey.design/post/1ebf70d4-0175-454d-8d74-31829305582f.png",
    "#sha1_content": "ba2d151e32114a894d342ed7408d970b9213e361",

    "extension": "png",
    "filename" : "1ebf70d4-0175-454d-8d74-31829305582f",
    "id"       : "background",
    "instance" : "misskey.design",
    "file"     : {"id": "1ebf70d4-0175-454d-8d74-31829305582f"},
    "user"     : {"id": "9bxksu5vqi"},
},

{
    "#url"     : "https://misskey.design/@blooddj@pawoo.net/notes",
    "#category": ("misskey", "misskey.design", "notes"),
    "#class"   : misskey.MisskeyNotesExtractor,
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
    "#results" : "https://file.misskey.design/post/a8d27901-24e1-42ab-b8a6-1e09c98c6f55.webp",
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
