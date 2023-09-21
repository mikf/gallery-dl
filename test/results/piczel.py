# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import piczel


__tests__ = (
{
    "#url"     : "https://piczel.tv/gallery/Bikupan",
    "#category": ("", "piczel", "user"),
    "#class"   : piczel.PiczelUserExtractor,
    "#range"   : "1-100",
    "#count"   : ">= 100",
},

{
    "#url"     : "https://piczel.tv/gallery/Lulena/1114",
    "#category": ("", "piczel", "folder"),
    "#class"   : piczel.PiczelFolderExtractor,
    "#count"   : ">= 4",
},

{
    "#url"     : "https://piczel.tv/gallery/image/7807",
    "#category": ("", "piczel", "image"),
    "#class"   : piczel.PiczelImageExtractor,
    "#pattern"     : r"https://(\w+\.)?piczel\.tv/static/uploads/gallery_image/32920/image/7807/1532236438-Lulena\.png",
    "#sha1_content": "df9a053a24234474a19bce2b7e27e0dec23bff87",

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

)
