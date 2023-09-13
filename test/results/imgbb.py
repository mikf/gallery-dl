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
    "#range"        : "1-80",
    "#sha1_url"     : "70afec9fcc3a6de62a6b644b487d892d8d47cf1a",
    "#sha1_metadata": "569e1d88ebdd27655387559cdf1cd526a3e1ab69",
},

{
    "#url"     : "https://ibb.co/album/i5PggF?sort=title_asc",
    "#category": ("", "imgbb", "album"),
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#range"        : "1-80",
    "#sha1_url"     : "afdf5fc95d8e09d77e8f44312f3e9b843987bb5a",
    "#sha1_metadata": "f090e14d0e5f7868595082b2c95da1309c84872d",
},

{
    "#url"     : "https://ibb.co/album/kYKpwF",
    "#comment" : "no user data (#471)",
    "#category": ("", "imgbb", "album"),
    "#class"   : imgbb.ImgbbAlbumExtractor,
    "#sha1_url": "ac0abcfcb89f4df6adc2f7e4ff872f3b03ef1bc7",

    "user": "",
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
    "#pattern" : r"https?://i\.ibb\.co/\w+/[^/?#]+",
    "#range"   : "1-80",
},

{
    "#url"     : "https://ibb.co/fUqh5b",
    "#category": ("", "imgbb", "image"),
    "#class"   : imgbb.ImgbbImageExtractor,
    "#pattern"     : r"https://i\.ibb\.co/g3kvx80/Arundel-Ireeman-5\.jpg",
    "#sha1_content": "c5a0965178a8b357acd8aa39660092918c63795e",

    "id"       : "fUqh5b",
    "title"    : "Arundel Ireeman 5",
    "url"      : "https://i.ibb.co/g3kvx80/Arundel-Ireeman-5.jpg",
    "width"    : 960,
    "height"   : 719,
    "user"     : "folkie",
    "extension": "jpg",
},

)
