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
    "#sha1_metadata": "f1ab5492adb6333409f3367566a6dd7110537e21",

    "album_id"   : "i5PggF",
    "album_name" : "British Scrap Book",
    "extension"  : "jpg",
    "id"         : r"re:^\w{7}$",
    "title"      : str,
    "url"        : r"re:https://i\.ibb\.co/\w{7}/[\w-]+\.jpg",
    "user"       : "folkie",
    "user_id"    : "GvFMGK",
    "displayname": "Folkie",
    "width"      : range(501, 1034),
    "height"     : range(335, 768),
    "size"       : range(74758, 439037),
},

{
    "#url"     : "https://ibb.co/album/i5PggF?sort=title_asc",
    "#comment" : "'sort' query argument",
    "#category": ("", "imgbb", "album"),
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#patten"       : r"https://i\.ibb\.co/\w{7}/[\w-]+\.jpg",
    "#count"        : 91,
    "#sha1_url"     : "cde36552cc132a27178f22a1b9aceaa4df7e1575",
    "#sha1_metadata": "b98bbb7671e31ebf9c7585fb9fc691b71bcdb546",
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
    "#comment" : "private",
    "#category": ("", "imgbb", "album"),
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://folkie.imgbb.com",
    "#category": ("", "imgbb", "user"),
    "#class"   : imgbb.ImgbbUserExtractor,
    "#patten"  : r"https://i\.ibb\.co/\w{7}/[\w-]+\.jpg",
    "#range"   : "1-80",
},

{
    "#url"     : "https://ibb.co/fUqh5b",
    "#category": ("", "imgbb", "image"),
    "#class"   : imgbb.ImgbbImageExtractor,
    "#pattern"     : r"https://i\.ibb\.co/g3kvx80/Arundel-Ireeman-5\.jpg",
    "#sha1_content": "c5a0965178a8b357acd8aa39660092918c63795e",

    "id"         : "fUqh5b",
    "title"      : "Arundel Ireeman 5",
    "url"        : "https://i.ibb.co/g3kvx80/Arundel-Ireeman-5.jpg",
    "width"      : 960,
    "height"     : 719,
    "user"       : "folkie",
    "user_id"    : "GvFMGK",
    "displayname": "Folkie",
    "extension"  : "jpg",
},

)
