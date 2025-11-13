# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import cyberdrop


__tests__ = (
{
    "#url"     : "https://cyberdrop.cr/a/8uE0wQiK",
    "#comment" : "",
    "#category": ("lolisafe", "cyberdrop", "album"),
    "#class"   : cyberdrop.CyberdropAlbumExtractor,
    "#pattern" : r"https://k1-cd.cdn.gigachad-cdn.ru/api/file/d/d1R0vW80T4BRt\?token=ey.+",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "album_id"     : "8uE0wQiK",
    "album_name"   : """test テスト "&>""",
    "album_size"   : 182,
    "auth_url"     : "https://api.cyberdrop.cr/api/file/auth/d1R0vW80T4BRt",
    "count"        : 1,
    "date"         : "dt:2023-11-26 00:00:00",
    "description"  : """test テスト "&>""",
    "extension"    : "png",
    "filename"     : "test-ãã¹ã--22->-xsaMaIQA",
    "id"           : "xsaMaIQA",
    "name"         : "test-ãã¹ã--22->",
    "num"          : 1,
    "size"         : 182,
    "slug"         : "d1R0vW80T4BRt",
    "thumbnail_url": "https://api.cyberdrop.cr/api/proxy/thumb/d1R0vW80T4BRt",
    "type"         : "image/png",
    "url"          : str,
},

{
    "#url"     : "https://cyberdrop.cr/a/HriMgbuf",
    "#comment" : "",
    "#category": ("lolisafe", "cyberdrop", "album"),
    "#class"   : cyberdrop.CyberdropAlbumExtractor,
    "#pattern" : (
        r"https://k1-cd.cdn.gigachad-cdn.ru/api/file/d/rln0wNQSY5iuA\?token=ey.+",
        r"https://k1-cd.cdn.gigachad-cdn.ru/api/file/d/cxSKzcj7Wxrrd\?token=ey.+",
        r"https://k1-cd.cdn.gigachad-cdn.ru/api/file/d/urLPkBXGuNfEg\?token=ey.+",
    ),

    "album_id"     : "HriMgbuf",
    "album_name"   : "animations",
    "album_size"   : 1090519,
    "auth_url"     : r"re:https://api.cyberdrop.cr/api/file/auth/\w+",
    "count"        : 3,
    "date"         : "dt:2023-11-26 00:00:00",
    "description"  : "animated stuff",
    "extension"    : {"gif", "webm"},
    "filename"     : str,
    "id"           : str,
    "name"         : str,
    "num"          : range(1, 3),
    "size"         : {798157, 143992, 147828},
    "slug"         : str,
    "thumbnail_url": r"re:https://api.cyberdrop.cr/api/proxy/thumb/\w+",
    "type"         : {"image/gif", "video/webm"},
    "url"          : str,
},

{
    "#url"     : "https://cyberdrop.me/a/8uE0wQiK",
    "#category": ("lolisafe", "cyberdrop", "album"),
    "#class"   : cyberdrop.CyberdropAlbumExtractor,
},

{
    "#url"     : "https://cyberdrop.cr/f/rln0wNQSY5iuA",
    "#category": ("lolisafe", "cyberdrop", "media"),
    "#class"   : cyberdrop.CyberdropMediaExtractor,
    "#pattern" : r"https://k1-cd.cdn.gigachad-cdn.ru/api/file/d/rln0wNQSY5iuA\?token=ey.+",
    "#sha1_content": "a546bdbc07d07f8e2c53e49e99736d5206f4da23",

    "album_id"     : "",
    "album_name"   : "",
    "album_size"   : -1,
    "auth_url"     : "https://api.cyberdrop.cr/api/file/auth/rln0wNQSY5iuA",
    "count"        : 1,
    "description"  : "",
    "extension"    : "gif",
    "filename"     : "danbooru_133128_049ebb917bb57589bca19155271a4200-cxEAcXkc",
    "id"           : "cxEAcXkc",
    "name"         : "danbooru_133128_049ebb917bb57589bca19155271a4200",
    "num"          : 1,
    "size"         : 143992,
    "slug"         : "rln0wNQSY5iuA",
    "thumbnail_url": "https://api.cyberdrop.cr/api/proxy/thumb/rln0wNQSY5iuA",
    "type"         : "image/gif",
    "url"          : r"re:https://k1-cd.cdn.gigachad-cdn.ru/api/file/d/rln0wNQSY5iuA\?token=ey.+",
},

{
    "#url"     : "https://cyberdrop.me/f/lHYBt9VAluZf6",
    "#category": ("lolisafe", "cyberdrop", "media"),
    "#class"   : cyberdrop.CyberdropMediaExtractor,
},

)
