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
    "#results"     : """https://brg-bk.cdn.gigachad-cdn.ru/test-テスト-"&>-QjgneIQv.png""",
    "#sha1_content": (
        "0c8768055e4e20e7c7259608b67799171b691140",
        "961b25d85b5f5bd18cbe3e847ac55925f14d0286",
    ),

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
    "slug"       : "test-テスト-\"&>-QjgneIQv.png",
    "num"        : 1,
},

{
    "#url"     : "https://bunkr.is/a/iXTTc1o2",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#results"     : (
        "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg",
    ),
    "#sha1_content": (
        "55998743751dfe008d0e95605114fcbfa7dc4de8",
        "caf7c3d3439d94e83b3c24ddaf5a3a48aa057519",
    ),

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
    "#count"   : 4,
},

{
    "#url"     : "https://bunkr.cr/a/Gm931jJz",
    "#comment" : "empty 'id', duplicate archive IDs (#6935)",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#count"   : 2,

    "id"    : "",
    "id_url": {"43478756", "43478551"},
    "slug"  : {"UPKDHBf0CvrCe", "zQgSePr1f4HZ2"},
    "uuid"  : "iso:uuid",
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
    "#url"     : "https://bunkr.cr/a/z5Xt6NqH",
    "#comment" : "filenames (#8150)",
    "#category": ("lolisafe", "bunkr", "album"),
    "#class"   : bunkr.BunkrAlbumExtractor,
    "#results" : (
        "https://beer.bunkr.ru/acba241d-c1e8-40c3-aa73-94daf75fcd13.jpg",
        "https://cake.bunkr.ru/e997f757-61dc-45be-bd61-b6998d813beb.jpg",
        "https://cake.bunkr.ru/72f1e20b-72a5-43b0-8ab2-472016e1d767.mp4",
    ),

    "album_id"  : "z5Xt6NqH",
    "album_name": "filename",
    "album_size": "1.82 MB",
    "count"     : 3,
    "date"      : "type:datetime",
    "extension" : {"jpg", "mp4"},
    "file"      : str,
    "id"        : "",
    "name"      : str,
    "num"       : range(1, 3),
    "id_url"    : {"53118207", "53118010", "53117871"},
    "size"      : {490885, 727670, 687238},
    "slug"      : {"Nzt1ID7lsgwR4", "Bu0e2k6gOB5di", "PwrDbEgQODSls"},
    "filename"  : {
        "'\"'",
        "😃",
        """filename: !"#$%&\'()*+,-.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]""",
    },
    "uuid"      : {
        "acba241d-c1e8-40c3-aa73-94daf75fcd13",
        "e997f757-61dc-45be-bd61-b6998d813beb",
        "72f1e20b-72a5-43b0-8ab2-472016e1d767",
    },
},

{
    "#url"     : "https://bunkr.black/i/image-sZrQUeOx.jpg",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#results"     : "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg",
    "#sha1_content": (
        "55998743751dfe008d0e95605114fcbfa7dc4de8",
        "caf7c3d3439d94e83b3c24ddaf5a3a48aa057519",
    ),

    "count"    : 1,
    "extension": "jpg",
    "file"     : "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg",
    "filename" : "image-sZrQUeOx",
    "id"       : "sZrQUeOx",
    "name"     : "image",
},

{
    "#url"     : "https://bunkr.cr/f/image-sZrQUeOx.jpg",
    "#comment" : "/f/ URL",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#results" : "https://mlk-bk.cdn.gigachad-cdn.ru/image-sZrQUeOx.jpg",
},

{
    "#url"     : "https://bunkrrr.org/d/dJuETSzKLrUps",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#results"     : "https://brg-bk.cdn.gigachad-cdn.ru/file-r5fmwjdd.zip",
    "#sha1_content": "102ddd7894fe39b3843098fc51f972a0af938f45",

    "count"    : 1,
    "extension": "zip",
    "file"     : "https://brg-bk.cdn.gigachad-cdn.ru/file-r5fmwjdd.zip",
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
    "#results" : "https://c.bunkr-cache.se/hAVFkYK1bLbSaaKq/27-03-2024-Rp-0FfrropA.mp4",
},

{
    "#url"     : "https://bunkr.site/f/wYGCKbGhSvuAW",
    "#comment" : "correct 'name' from HTML (#6790)",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#results" : "https://c.bunkr-cache.se/QlXezBjk2fCVVobM/80ca5405-8b8d-4f9f-8167-8b046bb9dc67.mp4",

    "id"       : "",
    "id_url"   : "41913002",
    "slug"     : "wYGCKbGhSvuAW",
    "uuid"     : "80ca5405-8b8d-4f9f-8167-8b046bb9dc67",
    "name"     : "0hwndshtfmj7hcbut1nd4_source",
    "filename" : "0hwndshtfmj7hcbut1nd4_source",
    "extension": "mp4",
},

{
    "#url"     : "https://bunkr.site/f/JEn5iQgYVYJfi",
    "#comment" : "file gone --- 403 error for main 'brg-bk.cdn.gigachad-cdn.ru' URL (#6732 #6972)",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#results"     : "https://brg-bk.cdn.gigachad-cdn.ru/IMG_47272f2c698d257fd22f4300ae98ec35929b-iEYVkLPQ.jpg",
    "#sha1_content": "f1c839743563828b250e48d485933a735a508527",

    "_http_headers": {
        "Referer": "https://get.bunkrr.su/file/29682239",
    },
    "extension": "jpg",
    "filename" : "IMG_47272f2c698d257fd22f4300ae98ec35929b-iEYVkLPQ",
    "id"       : "iEYVkLPQ",
    "id_url"   : "29682239",
    "name"     : "IMG_47272f2c698d257fd22f4300ae98ec35929b",
},

{
    "#url"     : "https://bunkr.pk/f/Nzt1ID7lsgwR4",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#results" : "https://beer.bunkr.ru/acba241d-c1e8-40c3-aa73-94daf75fcd13.jpg",

    "filename"   : "'\"'",
    "id"         : "",
    "id_url"     : "53118207",
    "name"       : "'\"'",
    "slug"       : "Nzt1ID7lsgwR4",
    "uuid"       : "acba241d-c1e8-40c3-aa73-94daf75fcd13",
},

{
    "#url"     : "https://bunkr.cr/f/mX1DBQooiUOJ9",
    "#comment" : "'album_...' metadata from '/f/' URL (#8405)",
    "#category": ("lolisafe", "bunkr", "media"),
    "#class"   : bunkr.BunkrMediaExtractor,
    "#results" : "https://rum.bunkr.ru/edf721b7-618b-4214-9305-845e1d210437.png",

    "album_id"  : "MwY4XLNV",
    "album_name": "foo & bar",
    "album_size": "3.54 MB",
    "count"     : 1,
    "extension" : "png",
    "filename"  : "danbooru_10113035_fe864be2aa86487e5b08c768be78b787",
    "id"        : "",
    "id_url"    : "54661720",
    "name"      : "danbooru_10113035_fe864be2aa86487e5b08c768be78b787",
    "num"       : 1,
    "slug"      : "mX1DBQooiUOJ9",
    "uuid"      : "edf721b7-618b-4214-9305-845e1d210437",
},

)
