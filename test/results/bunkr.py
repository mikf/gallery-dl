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
    "#urls"        : "https://i-burger.bunkr.ru/test-%E3%83%86%E3%82%B9%E3%83%88-%22%26%3E-QjgneIQv.png?download=true",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "album_id"   : "Lktg9Keq",
    "album_name" : "test テスト \"&>",
    "album_size" : "182 B",
    "count"      : 1,
    "extension"  : "png",
    "file"       : "https://i-burger.bunkr.ru/test-%E3%83%86%E3%82%B9%E3%83%88-%22%26%3E-QjgneIQv.png?download=true",
    "filename"   : "test-テスト-\"&>-QjgneIQv",
    "id"         : "QjgneIQv",
    "name"       : "test-テスト-\"&>",
    "num"        : 1,
},

{
    "#url"     : "https://bunkr.is/a/iXTTc1o2",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#urls"        : (
        "https://i-milkshake.bunkr.ru/image-sZrQUeOx.jpg?download=true",
    ),
    "#sha1_content": "caf7c3d3439d94e83b3c24ddaf5a3a48aa057519",

    "album_id"   : "iXTTc1o2",
    "album_name" : "test2",
    "album_size" : "534.6 KB",
    "count"      : 1,
    "filename"   : r"image-sZrQUeOx",
    "id"         : r"sZrQUeOx",
    "name"       : r"image",
    "num"        : 1,
},

{
    "#url"     : "https://bunkr.cat/a/j1G29CnD",
    "#comment" : "cdn12 .ru TLD (#4147)",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#pattern" : r"https://(i-)?meatballs.bunkr.ru/\w+",
    "#count"   : 7,
},

{
    "#url"     : "https://bunkr.ph/a/Lktg9Keq",
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.ps/a/Lktg9Keq",
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.pk/a/Lktg9Keq",
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.ax/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkrrr.org/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.ci/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.cr/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.fi/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
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
    "#url"     : "bunkr:http://example.org/a/Lktg9Keq",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
},

{
    "#url"     : "https://bunkr.black/i/image-sZrQUeOx.jpg",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"        : "https://i-milkshake.bunkr.ru/image-sZrQUeOx.jpg?download=true",
    "#sha1_content": "caf7c3d3439d94e83b3c24ddaf5a3a48aa057519",

    "count"    : 1,
    "extension": "jpg",
    "file"     : "https://i-milkshake.bunkr.ru/image-sZrQUeOx.jpg?download=true",
    "filename" : "image-sZrQUeOx",
    "id"       : "sZrQUeOx",
    "name"     : "image",
},

{
    "#url"     : "https://bunkrrr.org/d/dJuETSzKLrUps",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"        : "https://burger.bunkr.ru/file-r5fmwjdd.zip",
    "#sha1_content": "102ddd7894fe39b3843098fc51f972a0af938f45",

    "count"    : 1,
    "extension": "zip",
    "file"     : "https://burger.bunkr.ru/file-r5fmwjdd.zip",
    "filename" : "file-r5fmwjdd",
    "id"       : "r5fmwjdd",
    "name"     : "file",
},

)
