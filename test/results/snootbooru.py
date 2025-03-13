# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import szurubooru


__tests__ = (
{
    "#url"     : "https://snootbooru.com/posts/query=sport",
    "#category": ("szurubooru", "snootbooru", "tag"),
    "#class"   : szurubooru.SzurubooruTagExtractor,
    "#pattern" : r"https://snootbooru\.com/data/posts/\d+_[0-9a-f]{16}\.\w+",
    "#count"   : range(100, 300),
},

{
    "#url"     : "https://snootbooru.com/post/14511",
    "#category": ("szurubooru", "snootbooru", "post"),
    "#class"   : szurubooru.SzurubooruPostExtractor,
    "#urls"        : "https://snootbooru.com/data/posts/14511_e753313112755da6.png",
    "#sha1_content": "e69e61e61c5372514808480aae3a8e355c9cd6fb",

    "canvasHeight" : 1000,
    "canvasWidth"  : 1414,
    "checksum"     : "e69e61e61c5372514808480aae3a8e355c9cd6fb",
    "checksumMD5"  : "f4f4ddfcbdf367f466ede0980acb3d7d",
    "commentCount" : int,
    "comments"     : list,
    "contentUrl"   : "data/posts/14511_e753313112755da6.png",
    "creationTime" : "2023-12-02T01:11:01.433664Z",
    "date"         : "dt:2023-12-02 01:11:01",
    "extension"    : "png",
    "favoriteCount": int,
    "favoritedBy"  : list,
    "featureCount" : int,
    "fileSize"     : 270639,
    "filename"     : "14511_e753313112755da6",
    "flags"        : [],
    "hasCustomThumbnail": False,
    "id"           : 14511,
    "lastEditTime" : "2023-12-02T01:12:09.500217Z",
    "lastFeatureTime": None,
    "mimeType"     : "image/png",
    "noteCount"    : 0,
    "notes"        : [],
    "ownFavorite"  : False,
    "ownScore"     : 0,
    "pools"        : [],
    "relationCount": 0,
    "relations"    : [],
    "safety"       : "safe",
    "score"        : range(1, 10),
    "source"       : None,
    "tagCount"     : 3,
    "tags"         : [
        "transparent",
        "sport",
        "text",
    ],
    "tags_default" : [
        "sport",
        "text"
    ],
    "thumbnailUrl" : "data/generated-thumbnails/14511_e753313112755da6.jpg",
    "type"         : "image",
    "user"         : {
        "avatarUrl": "data/avatars/komp.png",
        "name": "komp"
    },
    "version"      : 2,
},

)
