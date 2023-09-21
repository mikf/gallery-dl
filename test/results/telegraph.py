# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import telegraph


__tests__ = (
{
    "#url"     : "https://telegra.ph/Telegraph-Test-03-28",
    "#category": ("", "telegraph", "gallery"),
    "#class"   : telegraph.TelegraphGalleryExtractor,
    "#pattern" : r"https://telegra\.ph/file/[0-9a-f]+\.png",

    "author"     : "mikf",
    "caption"    : r"re:test|",
    "count"      : 2,
    "date"       : "dt:2022-03-28 16:01:36",
    "description": "Just a test",
    "post_url"   : "https://telegra.ph/Telegraph-Test-03-28",
    "slug"       : "Telegraph-Test-03-28",
    "title"      : "Telegra.ph Test",
},

{
    "#url"     : "https://telegra.ph/森-03-28",
    "#category": ("", "telegraph", "gallery"),
    "#class"   : telegraph.TelegraphGalleryExtractor,
    "#pattern" : "https://telegra.ph/file/3ea79d23b0dd0889f215a.jpg",
    "#count"   : 1,

    "author"       : "&",
    "caption"      : "kokiri",
    "count"        : 1,
    "date"         : "dt:2022-03-28 16:31:26",
    "description"  : "コキリの森",
    "extension"    : "jpg",
    "filename"     : "3ea79d23b0dd0889f215a",
    "num"          : 1,
    "num_formatted": "1",
    "post_url"     : "https://telegra.ph/森-03-28",
    "slug"         : "森-03-28",
    "title"        : "\"森\"",
    "url"          : "https://telegra.ph/file/3ea79d23b0dd0889f215a.jpg",
},

{
    "#url"     : "https://telegra.ph/Vsyo-o-druzyah-moej-sestricy-05-27",
    "#category": ("", "telegraph", "gallery"),
    "#class"   : telegraph.TelegraphGalleryExtractor,
    "#pattern" : r"^https://pith1\.ru/uploads/posts/2019-12/\d+_\d+\.jpg$",
    "#sha1_url": "c1f3048e5d94bee53af30a8c27f70b0d3b15438e",

    "author"       : "Shotacon - заходи сюда",
    "caption"      : "",
    "count"        : 19,
    "date"         : "dt:2022-05-27 16:17:27",
    "description"  : "",
    "num_formatted": r"re:^\d{2}$",
    "post_url"     : "https://telegra.ph/Vsyo-o-druzyah-moej-sestricy-05-27",
    "slug"         : "Vsyo-o-druzyah-moej-sestricy-05-27",
    "title"        : "Всё о друзьях моей сестрицы",
},

{
    "#url"     : "https://telegra.ph/Disharmonica---Saber-Nero-02-21",
    "#category": ("", "telegraph", "gallery"),
    "#class"   : telegraph.TelegraphGalleryExtractor,
    "#pattern" : r"https://telegra\.ph/file/[0-9a-f]+\.(jpg|png)",

    "author"       : "cosmos",
    "caption"      : "",
    "count"        : 89,
    "date"         : "dt:2022-02-21 05:57:39",
    "description"  : "",
    "num_formatted": r"re:^\d{2}$",
    "post_url"     : "https://telegra.ph/Disharmonica---Saber-Nero-02-21",
    "slug"         : "Disharmonica---Saber-Nero-02-21",
    "title"        : "Disharmonica - Saber Nero",
},

)
