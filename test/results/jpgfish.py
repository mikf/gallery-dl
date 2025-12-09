# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import chevereto


__tests__ = (
{
    "#url"     : "https://jpg7.cr/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#results"     : "https://simp3.selti-delivery.ru/images/funnymeme.jpg",
    "#sha1_content": "098e5e9b17ad634358426e0ffd1c93871474d13c",

    "album"    : "",
    "album_id" : "",
    "album_slug": "",
    "date"     : "dt:2022-06-05 03:24:25",
    "extension": "jpg",
    "filename" : "funnymeme",
    "id"       : "LecXGS",
    "url"      : "https://simp3.selti-delivery.ru/images/funnymeme.jpg",
    "user"     : "exearco",
},

{
    "#url"     : "https://jpg4.su/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#results" : "https://simp3.selti-delivery.ru/images/funnymeme.jpg",

    "album"    : "",
    "date"     : "dt:2022-06-05 03:24:25",
    "extension": "jpg",
    "filename" : "funnymeme",
    "id"       : "LecXGS",
    "url"      : "https://simp3.selti-delivery.ru/images/funnymeme.jpg",
    "user"     : "exearco",
},

{
    "#url"     : "https://jpg6.su/img/LecXGS/",
    "#comment" : "image ID without name (#8307)",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#results"     : "https://simp3.selti-delivery.ru/images/funnymeme.jpg",
    "#sha1_content": "098e5e9b17ad634358426e0ffd1c93871474d13c",

    "album"    : "",
    "date"     : "dt:2022-06-05 03:24:25",
    "extension": "jpg",
    "filename" : "funnymeme",
    "id"       : "LecXGS",
    "url"      : str,
    "user"     : "exearco",
},

{
    "#url"     : "https://jpg.church/img/auCruA",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#results" : "https://simp2.selti-delivery.ru/hannahowo_00457.jpg",

    "album"     : "401-500",
    "album_id"  : "atYaG",
    "album_slug": "401-500",
    "date"      : "dt:2022-03-23 13:50:52",
    "id"        : "auCruA",
},

{
    "#url"     : "https://jpg1.su/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://jpeg.pet/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://jpg.pet/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://jpg.fishing/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://jpg.fish/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://jpg.church/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://www.jpg6.su/img/funnymeme.LecXGS",
    "#category": ("chevereto", "jpgfish", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://jpg1.su/album/CDilP/?sort=date_desc&page=1",
    "#category": ("chevereto", "jpgfish", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#count"   : 2,

    "album"     : "funny meme album",
    "album_id"  : "CDilP",
    "album_slug": "funny-meme-album",
    "count"     : 2,
    "num"       : range(1, 2),
},

{
    "#url"     : "https://jpg.fishing/a/gunggingnsk.N9OOI",
    "#category": ("chevereto", "jpgfish", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#count"   : 114,

    "album"     : "Gunggingnsk OF",
    "album_id"  : "N9OOI",
    "album_slug": "gunggingnsk",
    "count"     : 114,
    "num"       : range(1, 114),
},

{
    "#url"     : "https://jpg.fish/a/101-200.aNJ6A/",
    "#category": ("chevereto", "jpgfish", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#count"   : 100,

    "album"     : "101-200",
    "album_id"  : "aNJ6A",
    "album_slug": "101-200",
    "count"     : 100,
    "num"       : range(1, 100),
},

{
    "#url"     : "https://jpg.church/a/hannahowo.aNTdH/sub",
    "#category": ("chevereto", "jpgfish", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#count"   : 606,

    "album"     : "re:([1-5]0)?1-[1-6]00",
    "album_id"  : str,
    "album_slug": str,
    "count"     : {100, 106},
    "num"       : range(1, 106),
},

{
    "#url"     : "https://jpeg.pet/album/CDilP/?sort=date_desc&page=1",
    "#category": ("chevereto", "jpgfish", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
},

{
    "#url"     : "https://jpg.pet/album/CDilP/?sort=date_desc&page=1",
    "#category": ("chevereto", "jpgfish", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
},

{
    "#url"     : "https://jpg1.su/exearco",
    "#category": ("chevereto", "jpgfish", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://jpg.church/exearco/albums",
    "#category": ("chevereto", "jpgfish", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://jpeg.pet/exearco",
    "#category": ("chevereto", "jpgfish", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

{
    "#url"     : "https://jpg.pet/exearco",
    "#category": ("chevereto", "jpgfish", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

{
    "#url"     : "https://jpg.fishing/exearco",
    "#category": ("chevereto", "jpgfish", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

{
    "#url"     : "https://jpg.fish/exearco",
    "#category": ("chevereto", "jpgfish", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

{
    "#url"     : "https://jpg.church/exearco",
    "#category": ("chevereto", "jpgfish", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

)
