# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bunkr


__tests__ = (
{
    "#url"     : "https://bunkrr.su/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#pattern"     : r"https://cdn\.bunkr\.ru/test-テスト-\"&>-QjgneIQv\.png",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "album_id"  : "Lktg9Keq",
    "album_name": "test テスト \"&>",
    "count"     : 1,
    "filename"  : "test-テスト-\"&>-QjgneIQv",
    "id"        : "QjgneIQv",
    "name"      : "test-テスト-\"&>",
    "num"       : int,
},

{
    "#url"     : "https://app.bunkr.ru/a/ptRHaCn2",
    "#comment" : "mp4 (#2239)",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#pattern"     : r"https://media-files\.bunkr\.ru/_-RnHoW69L\.mp4",
    "#sha1_content": "80e61d1dbc5896ae7ef9a28734c747b28b320471",
},

{
    "#url"     : "https://bunkr.is/a/iXTTc1o2",
    "#comment" : "cdn4",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#pattern"     : r"https://(cdn|media-files)4\.bunkr\.ru/",
    "#sha1_content": "da29aae371b7adc8c5ef8e6991b66b69823791e8",

    "album_id"   : "iXTTc1o2",
    "album_name" : "test2",
    "album_size" : "691.1 KB",
    "count"      : 2,
    "description": "072022",
    "filename"   : r"re:video-wFO9FtxG|image-sZrQUeOx",
    "id"         : r"re:wFO9FtxG|sZrQUeOx",
    "name"       : r"re:video|image",
    "num"        : int,
},

{
    "#url"     : "https://bunkrr.su/a/j1G29CnD",
    "#comment" : "cdn12 .ru TLD (#4147)",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#pattern" : r"https://(cdn12.bunkr.ru|media-files12.bunkr.la)/\w+",
    "#count"   : 8,
},

{
    "#url"     : "https://bunkrr.su/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.la/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.su/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.ru/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.is/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.to/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

)
