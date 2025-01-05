# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import piczel


__tests__ = (
{
    "#url"  : "https://piczel.tv/gallery/Bikupan",
    "#class": piczel.PiczelUserExtractor,
    "#range": "1-100",
    "#count": ">= 100",
},

{
    "#url"  : "https://piczel.tv/gallery/Lulena/1114",
    "#class": piczel.PiczelFolderExtractor,
    "#urls" : (
        "https://piczel.tv/static/uploads/gallery_image/32920/image/11194/1544126403-Lulena.png",
        "https://piczel.tv/static/uploads/gallery_image/32920/image/8008/1533616260-Lulena.png",
        "https://piczel.tv/static/uploads/plain_image/32920/image/3761/3761-Lulena.png",
        "https://piczel.tv/static/uploads/plain_image/32920/image/3762/3762-Lulena.png",
        "https://piczel.tv/static/uploads/gallery_image/32920/image/7991/1533513024-Lulena.png",
        "https://piczel.tv/static/uploads/gallery_image/32920/image/7806/1532236348-Lulena.png",
        "https://piczel.tv/static/uploads/gallery_image/32920/image/7800/1532235785-Lulena.png",
    ),

    "folder_id": 1114,
},

{
    "#url"  : "https://piczel.tv/gallery/image/7807",
    "#class": piczel.PiczelImageExtractor,
    "#urls"        : "https://piczel.tv/static/uploads/gallery_image/32920/image/7807/1532236438-Lulena.png",
    "#sha1_content": "df9a053a24234474a19bce2b7e27e0dec23bff87",

    "count"           : 1,
    "created_at"      : "2018-07-22T05:13:58.000Z",
    "date"            : "dt:2018-07-22 05:13:58",
    "description"     : None,
    "extension"       : "png",
    "favorites_count" : int,
    "folder_id"       : 1113,
    "id"              : 7807,
    "is_flash"        : False,
    "is_video"        : False,
    "multi"           : False,
    "nsfw"            : False,
    "num"             : 0,
    "password_protected": False,
    "tags"            : [
        "fanart",
        "commission",
        "altair",
        "recreators",
    ],
    "title"           : "Altair",
    "user"            : dict,
    "views"           : int,
},

{
    "#url"    : "https://piczel.tv/gallery/image/8008",
    "#comment": "multi",
    "#class"  : piczel.PiczelImageExtractor,
    "#urls"   : (
        "https://piczel.tv/static/uploads/gallery_image/32920/image/8008/1533616260-Lulena.png",
        "https://piczel.tv/static/uploads/plain_image/32920/image/3761/3761-Lulena.png",
        "https://piczel.tv/static/uploads/plain_image/32920/image/3762/3762-Lulena.png",
    ),

    "count"      : 3,
    "created_at" : "2018-08-07T04:31:00.000Z",
    "curated"    : False,
    "date"       : "dt:2018-08-07 04:31:00",
    "description": "8/7/18",
    "extension"  : "png",
    "favorites_count": range(3, 10),
    "folder_id"  : 1114,
    "width"      : None,
    "height"     : None,
    "id"         : 8008,
    "is_flash"   : False,
    "is_video"   : False,
    "multi"      : True,
    "nsfw"       : True,
    "num"        : {0, 1, 2},
    "password_protected"  : False,
    "published_at"        : "2018-08-07T04:31:00.000Z",
    "rendered_description": "<p>8/7/18</p>",
    "status"     : "published",
    "thumbnail"  : None,
    "title"      : "❤",
    "views"      : 314,
    "tags"       : [
        "original",
        "Orc",
        "tanlines",
    ],
    "user"       : {
        "follower_count": range(15, 25),
        "id"      : 32920,
        "premium?": False,
        "role"    : "user",
        "username": "Lulena",
    },
},

)
