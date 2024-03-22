# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bunkr


__tests__ = (
{
    "#url"     : "https://bunkr.sk/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#urls"        : "https://i-burger.bunkr.ru/test-テスト-\"&>-QjgneIQv.png",
    "#sha1_content": "961b25d85b5f5bd18cbe3e847ac55925f14d0286",

    "album_id"   : "Lktg9Keq",
    "album_name" : "test テスト \"&>",
    "album_size" : "182 B",
    "count"      : 1,
    "extension"  : "png",
    "file"       : "https://i-burger.bunkr.ru/test-テスト-\"&>-QjgneIQv.png",
    "filename"   : "test-テスト-\"&>-QjgneIQv",
    "id"         : "QjgneIQv",
    "name"       : "test-テスト-\"&>",
    "num"        : 1,
},

{
    "#url"     : "https://bunkr.is/a/iXTTc1o2",
    "#comment" : "cdn4",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#urls"        : (
        "https://i-milkshake.bunkr.ru/image-sZrQUeOx.jpg",
        "https://burger.bunkr.ru/video-gLn1hgpw.mp4",
    ),
    "#sha1_content": "80914b8190ad001662f64e3b0b9c02ea3872c584",

    "album_id"   : "iXTTc1o2",
    "album_name" : "test2",
    "album_size" : "561.6 KB",
    "count"      : 2,
    "filename"   : r"re:video-gLn1hgpw|image-sZrQUeOx",
    "id"         : r"re:gLn1hgpw|sZrQUeOx",
    "name"       : r"re:video|image",
    "num"        : range(1, 2),
},

{
    "#url"     : "https://bunkr.cat/a/j1G29CnD",
    "#comment" : "cdn12 .ru TLD (#4147)",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#pattern" : r"https://(i-)?meatballs.bunkr.ru/\w+",
    "#count"   : 9,
},

{
    "#url"     : "https://bunkr.si/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.ac/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.media/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.site/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.ws/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkrr.ru/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
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

{
    "#url"     : "https://bunkr.black/i/image-sZrQUeOx.jpg",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"        : "https://i-milkshake.bunkr.ru/image-sZrQUeOx.jpg",
    "#sha1_content": "55998743751dfe008d0e95605114fcbfa7dc4de8",

    "count"    : 1,
    "extension": "jpg",
    "file"     : "https://i-milkshake.bunkr.ru/image-sZrQUeOx.jpg",
    "filename" : "image-sZrQUeOx",
    "id"       : "sZrQUeOx",
    "name"     : "image",
},

{
    "#url"     : "https://bunkr.red/v/MY5aa4cLO7jN5",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"        : "https://burger.bunkr.ru/video-gLn1hgpw.mp4",
    "#sha1_content": "f7a2ab24766a15ceffff1b07bada432b13ff8e5b",

    "count"    : 1,
    "extension": "mp4",
    "file"     : "https://burger.bunkr.ru/video-gLn1hgpw.mp4",
    "filename" : "video-gLn1hgpw",
    "id"       : "gLn1hgpw",
    "name"     : "video",
},

)
