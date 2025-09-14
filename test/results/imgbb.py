# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imgbb
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://ibb.co/album/i5PggF",
    "#category": ("", "imgbb", "album"),
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#patten"       : r"https://i\.ibb\.co/\w{7}/[\w-]+\.jpg",
    "#count"        : 91,
    "#sha1_url"     : "efe7e5a76531436e3b82c87e4ebd34c4dfeb484c",

    "extension": "jpg",
    "filename" : str,
    "id"       : r"re:^\w{7}$",
    "title"    : str,
    "url"      : r"re:https://i\.ibb\.co/\w{7}/[\w-]+\.jpg",
    "width"    : range(501, 1034),
    "height"   : range(335, 768),
    "size"     : range(74758, 439037),
    "mime"     : "image/jpeg",
    "album"    : {
        "count"      : 91,
        "description": "Brief description of this album",
        "id"         : "cgJrwc",
        "title"      : "British Scrap Book",
        "url"        : "https://ibb.co/album/cgJrwc",
    },
    "user"     : {
        "id"        : "GvFMGK",
        "name"      : "Folkie",
        "url"       : "https://folkie.imgbb.com/",
        "url_albums": "https://folkie.imgbb.com/albums",
        "username"  : "folkie",
    },
},

{
    "#url"     : "https://ibb.co/album/cgJrwc?sort=name_asc",
    "#comment" : "'sort' query argument",
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#patten"  : r"https://i\.ibb\.co/\w{7}/[\w-]+\.jpg",
    "#count"   : 91,
    "#sha1_url": "a1bf67f74a6644b360a989a887ff413fd4eab2a6",
},

{
    "#url"     : "https://ibb.co/album/kYKpwF",
    "#comment" : "no user data (#471)",
    "#category": ("", "imgbb", "album"),
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#sha1_url": "ac0abcfcb89f4df6adc2f7e4ff872f3b03ef1bc7",

    "displayname": "",
    "user"       : "",
    "user_id"    : "",
},

{
    "#url"     : "https://ibb.co/album/hqgWrF",
    "#comment" : "private / That page doesn't exist",
    "#category": ("", "imgbb", "album"),
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://ibb.co/album/jyYWqL",
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#results" : "https://i.ibb.co/1J4mTWzQ/test.png",

    "extension": "png",
    "filename" : "test",
    "height"   : 32,
    "id"       : "bRGKX9bm",
    "mime"     : "image/png",
    "name"     : "test.png",
    "size"     : 182,
    "title"    : "test",
    "url"      : "https://i.ibb.co/1J4mTWzQ/test.png",
    "width"    : 64,
    "album"    : {
        "count"      : 1,
        "id"         : "jyYWqL",
        "title"      : "test-テスト-\"&> Album",
        "url"        : "https://ibb.co/album/jyYWqL",
        "description": """test-テスト-"&>\nDescription""",
    },
    "user"     : {
        "id"        : "nrFBYw",
        "name"      : "Gdldev",
        "url"       : "https://gdldev.imgbb.com/",
        "url_albums": "https://gdldev.imgbb.com/albums",
        "username"  : "gdldev",
    },
},

{
    "#url"     : "https://folkie.imgbb.com",
    "#class"   : imgbb.ImgbbUserExtractor,
    "#auth"    : True,
    "#patten"  : r"https://i\.ibb\.co/\w{7}/[\w-]+\.jpg",
    "#range"   : "1-80",

},

{
    "#url"     : "https://folkie.imgbb.com",
    "#class"   : imgbb.ImgbbUserExtractor,
    "#auth"     : False,
    "#exception": exception.AuthRequired,
},

{
    "#url"     : "https://gdldev.imgbb.com/",
    "#class"   : imgbb.ImgbbUserExtractor,
    "#results" : "https://i.ibb.co/1J4mTWzQ/test.png",

    "extension": "png",
    "filename" : "test",
    "height"   : 32,
    "id"       : "bRGKX9bm",
    "mime"     : "image/png",
    "name"     : "test.png",
    "size"     : 182,
    "title"    : "test",
    "url"      : "https://i.ibb.co/1J4mTWzQ/test.png",
    "width"    : 64,
    "user"     : {
        "id"        : "nrFBYw",
        "name"      : "Gdldev",
        "url"       : "https://gdldev.imgbb.com/",
        "url_albums": "https://gdldev.imgbb.com/albums",
        "username"  : "gdldev",
    },
},

{
    "#url"     : "https://ibb.co/fUqh5b",
    "#class"   : imgbb.ImgbbImageExtractor,
    "#auth"    : False,
    "#results"     : "https://i.ibb.co/g3kvx80/Arundel-Ireeman-5.jpg",
    "#sha1_content": "c5a0965178a8b357acd8aa39660092918c63795e",

    "id"       : "qdT0v8H",
    "title"    : "Arundel Ireeman 5",
    "url"      : "https://i.ibb.co/g3kvx80/Arundel-Ireeman-5.jpg",
    "width"    : 960,
    "height"   : 719,
    "filename" : "Arundel-Ireeman-5",
    "extension": "jpg",
    "date"     : "dt:2017-09-29 13:50:25",
    "album"    : {
        "id"   : "cgJrwc",
        "title": "British Scrap Book",
    },
    "user"     : {
        "id"        : "GvFMGK",
        "name"      : "Folkie",
        "url"       : "https://folkie.imgbb.com/",
        "url_albums": "https://folkie.imgbb.com/albums",
        "username"  : "folkie",
    },
},

{
    "#url"     : "https://ibb.co/bRGKX9bm",
    "#class"   : imgbb.ImgbbImageExtractor,
    "#auth"    : False,
    "#results" : "https://i.ibb.co/1J4mTWzQ/test.png",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "date"     : "dt:2025-07-30 20:05:06",
    "extension": "png",
    "filename" : "test",
    "height"   : 32,
    "id"       : "bRGKX9bm",
    "title"    : "test",
    "url"      : "https://i.ibb.co/1J4mTWzQ/test.png",
    "width"    : 64,
    "album"    : {
        "id"   : "jyYWqL",
        "title": "test-テスト-\"&> Album",
    },
    "user"     : {
        "id"        : "nrFBYw",
        "name"      : "Gdldev",
        "url"       : "https://gdldev.imgbb.com/",
        "url_albums": "https://gdldev.imgbb.com/albums",
        "username"  : "gdldev",
    },
},

)
