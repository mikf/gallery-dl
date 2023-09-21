# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import jpgfish


__tests__ = (
{
    "#url"     : "https://jpg1.su/img/funnymeme.LecXGS",
    "#category": ("", "jpgfish", "image"),
    "#class"   : jpgfish.JpgfishImageExtractor,
    "#pattern"     : r"https://simp3\.jpg\.church/images/funnymeme\.jpg",
    "#sha1_content": "098e5e9b17ad634358426e0ffd1c93871474d13c",

    "album"    : "",
    "extension": "jpg",
    "filename" : "funnymeme",
    "id"       : "LecXGS",
    "url"      : "https://simp3.jpg.church/images/funnymeme.jpg",
    "user"     : "exearco",
},

{
    "#url"     : "https://jpg.church/img/auCruA",
    "#category": ("", "jpgfish", "image"),
    "#class"   : jpgfish.JpgfishImageExtractor,
    "#pattern" : r"https://simp2\.jpg\.church/hannahowo_00457\.jpg",

    "album": "401-500",
},

{
    "#url"     : "https://jpeg.pet/img/funnymeme.LecXGS",
    "#category": ("", "jpgfish", "image"),
    "#class"   : jpgfish.JpgfishImageExtractor,
},

{
    "#url"     : "https://jpg.pet/img/funnymeme.LecXGS",
    "#category": ("", "jpgfish", "image"),
    "#class"   : jpgfish.JpgfishImageExtractor,
},

{
    "#url"     : "https://jpg.fishing/img/funnymeme.LecXGS",
    "#category": ("", "jpgfish", "image"),
    "#class"   : jpgfish.JpgfishImageExtractor,
},

{
    "#url"     : "https://jpg.fish/img/funnymeme.LecXGS",
    "#category": ("", "jpgfish", "image"),
    "#class"   : jpgfish.JpgfishImageExtractor,
},

{
    "#url"     : "https://jpg.church/img/funnymeme.LecXGS",
    "#category": ("", "jpgfish", "image"),
    "#class"   : jpgfish.JpgfishImageExtractor,
},

{
    "#url"     : "https://jpg1.su/album/CDilP/?sort=date_desc&page=1",
    "#category": ("", "jpgfish", "album"),
    "#class"   : jpgfish.JpgfishAlbumExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://jpg.fishing/a/gunggingnsk.N9OOI",
    "#category": ("", "jpgfish", "album"),
    "#class"   : jpgfish.JpgfishAlbumExtractor,
    "#count"   : 114,
},

{
    "#url"     : "https://jpg.fish/a/101-200.aNJ6A/",
    "#category": ("", "jpgfish", "album"),
    "#class"   : jpgfish.JpgfishAlbumExtractor,
    "#count"   : 100,
},

{
    "#url"     : "https://jpg.church/a/hannahowo.aNTdH/sub",
    "#category": ("", "jpgfish", "album"),
    "#class"   : jpgfish.JpgfishAlbumExtractor,
    "#count"   : 606,
},

{
    "#url"     : "https://jpeg.pet/album/CDilP/?sort=date_desc&page=1",
    "#category": ("", "jpgfish", "album"),
    "#class"   : jpgfish.JpgfishAlbumExtractor,
},

{
    "#url"     : "https://jpg.pet/album/CDilP/?sort=date_desc&page=1",
    "#category": ("", "jpgfish", "album"),
    "#class"   : jpgfish.JpgfishAlbumExtractor,
},

{
    "#url"     : "https://jpg1.su/exearco",
    "#category": ("", "jpgfish", "user"),
    "#class"   : jpgfish.JpgfishUserExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://jpg.church/exearco/albums",
    "#category": ("", "jpgfish", "user"),
    "#class"   : jpgfish.JpgfishUserExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://jpeg.pet/exearco",
    "#category": ("", "jpgfish", "user"),
    "#class"   : jpgfish.JpgfishUserExtractor,
},

{
    "#url"     : "https://jpg.pet/exearco",
    "#category": ("", "jpgfish", "user"),
    "#class"   : jpgfish.JpgfishUserExtractor,
},

{
    "#url"     : "https://jpg.fishing/exearco",
    "#category": ("", "jpgfish", "user"),
    "#class"   : jpgfish.JpgfishUserExtractor,
},

{
    "#url"     : "https://jpg.fish/exearco",
    "#category": ("", "jpgfish", "user"),
    "#class"   : jpgfish.JpgfishUserExtractor,
},

{
    "#url"     : "https://jpg.church/exearco",
    "#category": ("", "jpgfish", "user"),
    "#class"   : jpgfish.JpgfishUserExtractor,
},

)
