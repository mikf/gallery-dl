# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import cyberdrop


__tests__ = (
{
    "#url"     : "https://cyberdrop.me/a/8uE0wQiK",
    "#category": ("lolisafe", "cyberdrop", "album"),
    "#class"   : cyberdrop.CyberdropAlbumExtractor,
    "#pattern"     : r"https://\w+\.cyberdrop\.ch/api/file/d/yyK9y8xpQK5dP\?token=ey.+",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "album_id"    : "8uE0wQiK",
    "album_name"  : "test テスト \"&>",
    "album_size"  : 182,
    "count"       : 1,
    "date"        : "dt:2023-11-26 00:00:00",
    "description" : "test テスト \"&>",
    "extension"   : "png",
    "filename"    : "test-ãã¹ã--22->-rwU3x9LU",
    "id"          : "rwU3x9LU",
    "name"        : "test-ãã¹ã--22->",
    "num"         : 1,
    "size"        : 182,
    "slug"        : "yyK9y8xpQK5dP",
    "thumbnail_url": str,
    "type"        : "image/png",
    "url"         : str,
},

{
    "#url"     : "https://cyberdrop.me/a/HriMgbuf",
    "#category": ("lolisafe", "cyberdrop", "album"),
    "#class"   : cyberdrop.CyberdropAlbumExtractor,
    "#pattern" : r"https://\w+\.cyberdrop\.ch/api/file/d/\w+\?token=ey.+",
    "#count"   : 3,

    "album_id"    : "HriMgbuf",
    "album_name"  : "animations",
    "album_size"  : 1090519,
    "count"       : 3,
    "date"        : "dt:2023-11-26 00:00:00",
    "description" : "animated stuff",
    "extension"   : r"re:gif|webm",
    "filename"    : r"re:danbooru_\d+_\w+-\w+",
    "id"          : str,
    "name"        : r"re:danbooru_\d+_\w+",
    "num"         : range(1, 3),
    "size"        : int,
    "slug"        : str,
    "thumbnail_url": str,
    "type"        : r"re:image/gif|video/webm",
    "url"         : str,
},

{
    "#url"     : "https://cyberdrop.me/f/lHYBt9VAluZf6",
    "#category": ("lolisafe", "cyberdrop", "media"),
    "#class"   : cyberdrop.CyberdropMediaExtractor,
    "#pattern"     : r"https://k1-cd\.cdn\.gigachad-cdn\.ru/api/file/d/lHYBt9VAluZf6\?token=ey.+",
    "#count"       : 1,
    "#sha1_content": "a546bdbc07d07f8e2c53e49e99736d5206f4da23",

    "album_id"     : "",
    "album_name"   : "",
    "album_size"   : -1,
    "auth_url"     : "https://api.cyberdrop.me/api/file/auth/lHYBt9VAluZf6",
    "count"        : 1,
    "description"  : "",
    "extension"    : "gif",
    "filename"     : "danbooru_133128_049ebb917bb57589bca19155271a4200-rrhV0I30",
    "id"           : "rrhV0I30",
    "name"         : "danbooru_133128_049ebb917bb57589bca19155271a4200",
    "num"          : 1,
    "size"         : 143992,
    "slug"         : "lHYBt9VAluZf6",
    "thumbnail_url": "https://api.cyberdrop.me/api/proxy/thumb/lHYBt9VAluZf6",
    "type"         : "image/gif",
    "url"          : str,
},

)
