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
    "#urls"        : "https://brg-bk.cdn.gigachad-cdn.ru/test-%E3%83%86%E3%82%B9%E3%83%88-%22%26%3E-QjgneIQv.png?n=test-%E3%83%86%E3%82%B9%E3%83%88-%22%26%3E.png",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "album_id"   : "Lktg9Keq",
    "album_name" : "test テスト \"&>",
    "album_size" : "182 bytes",
    "count"      : 1,
    "extension"  : "png",
    "file"       : str,
    "filename"   : "test-テスト-\"&>-QjgneIQv",
    "id"         : "QjgneIQv",
    "id_url"     : "1044478",
    "name"       : "test-テスト-\"&>",
    "num"        : 1,
},

{
    "#url"     : "https://bunkr.is/a/iXTTc1o2",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#urls"        : (
        "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg?n=image.jpg",
    ),
    "#sha1_content": "55998743751dfe008d0e95605114fcbfa7dc4de8",

    "album_id"   : "iXTTc1o2",
    "album_name" : "test2",
    "album_size" : "534.61 KB",
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
    "#range"   : "5-",
    "#count"   : 3,
},

{
    "#url"     : "https://bunkr.cr/a/Gm931jJz",
    "#comment" : "empty 'id', duplicate archive IDs (#6935)",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#count"   : 2,

    "id"    : "",
    "id_url": {"UPKDHBf0CvrCe", "zQgSePr1f4HZ2"},
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
    "#urls"        : "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg?n=image.jpg",
    "#sha1_content": "55998743751dfe008d0e95605114fcbfa7dc4de8",

    "count"    : 1,
    "extension": "jpg",
    "file"     : "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg?n=image.jpg",
    "filename" : "image-sZrQUeOx",
    "id"       : "sZrQUeOx",
    "name"     : "image",
},

{
    "#url"     : "https://bunkr.cr/f/image-sZrQUeOx.jpg",
    "#comment" : "/f/ URL",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"    : "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg?n=image.jpg",
},

{
    "#url"     : "https://bunkrrr.org/d/dJuETSzKLrUps",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"        : "https://brg-bk.cdn.gigachad-cdn.ru/file-r5fmwjdd.zip?n=file.zip",
    "#sha1_content": "102ddd7894fe39b3843098fc51f972a0af938f45",

    "count"    : 1,
    "extension": "zip",
    "file"     : "https://brg-bk.cdn.gigachad-cdn.ru/file-r5fmwjdd.zip?n=file.zip",
    "filename" : "file-r5fmwjdd",
    "id"       : "r5fmwjdd",
    "id_url"   : "38792076",
    "name"     : "file",
},

{
    "#url"     : "https://bunkr.ph/v/rEeTUL8MXR17A",
    "#comment" : "redirect to '/f/rEeTUL8MXR17A' (#6790)",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"    : "https://meatballs.bunkr.ru/27-03-2024-Rp-0FfrropA.mp4",
},

{
    "#url"     : "https://bunkr.site/f/wYGCKbGhSvuAW",
    "#comment" : "correct 'name' from HTML (#6790)",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"    : "https://kebab.bunkr.ru/80ca5405-8b8d-4f9f-8167-8b046bb9dc67.mp4",

    "id"       : "",
    "id_url"   : "wYGCKbGhSvuAW",
    "name"     : "0hwndshtfmj7hcbut1nd4_source",
    "filename" : "0hwndshtfmj7hcbut1nd4_source",
    "extension": "mp4",
},

{
    "#url"     : "https://bunkr.site/f/JEn5iQgYVYJfi",
    "#comment" : "file gone --- 403 error for main 'brg-bk.cdn.gigachad-cdn.ru' URL (#6732 #6972)",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#urls"        : "https://brg-bk.cdn.gigachad-cdn.ru/IMG_47272f2c698d257fd22f4300ae98ec35929b-iEYVkLPQ.jpg?n=IMG_47272f2c698d257fd22f4300ae98ec35929b.jpg",
    "#sha1_content": "f1c839743563828b250e48d485933a735a508527",

    "_fallback": (
        "https://i-burger.bunkr.ru/IMG_47272f2c698d257fd22f4300ae98ec35929b-iEYVkLPQ.jpg",
    ),
    "_http_headers": {
        "Referer": "https://get.bunkrr.su/file/29682239",
    },
    "extension": "jpg",
    "filename" : "IMG_47272f2c698d257fd22f4300ae98ec35929b-iEYVkLPQ",
    "id"       : "iEYVkLPQ",
    "id_url"   : "29682239",
    "name"     : "IMG_47272f2c698d257fd22f4300ae98ec35929b",
},

)
