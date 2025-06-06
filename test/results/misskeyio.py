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
    "#pattern" : r"https://(media.misskeyusercontent.com|s\d+\.arkjp\.net)/(misskey|io)/[\w-]+\.\w+",
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://misskey.io/@lithla/avatar",
    "#category": ("misskey", "misskey.io", "avatar"),
    "#class"   : misskey.MisskeyAvatarExtractor,
    "#urls"    : "https://media.misskeyusercontent.jp/io/d84e09f8-99b7-423a-9229-78ba65ab8a82.gif",
    "#sha1_content": "375af4d302a4aef0bc8fc3f15b2c75ec952ac086",

    "extension": "gif",
    "filename" : "d84e09f8-99b7-423a-9229-78ba65ab8a82",
    "id"       : "avatar",
    "instance" : "misskey.io",
    "file"     : {"id": "d84e09f8-99b7-423a-9229-78ba65ab8a82"},
    "user"     : {"id": "9bhpt59w5k"},
},

{
    "#url"     : "https://misskey.io/@lithla/banner",
    "#category": ("misskey", "misskey.io", "background"),
    "#class"   : misskey.MisskeyBackgroundExtractor,
    "#urls"    : "https://media.misskeyusercontent.jp/io/ddea6f5f-9cde-42ff-8e0b-dafbfa9cca9b.png",
    "#sha1_content": "02e1d33a7aa03d8e63baa82ea6d75c7d5de80112",

    "extension": "png",
    "filename" : "ddea6f5f-9cde-42ff-8e0b-dafbfa9cca9b",
    "id"       : "background",
    "instance" : "misskey.io",
    "file"     : {"id": "ddea6f5f-9cde-42ff-8e0b-dafbfa9cca9b"},
    "user"     : {"id": "9bhpt59w5k"},
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
    "#pattern" : r"https://(media\.misskeyusercontent\.com|s\d+\.arkjp\.net)/misskey/[\w-]+\.\w+",
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
