# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pictoa

__tests__ = (
{
    "#url"     : "https://www.pictoa.com/albums/anna-kendrick-busty-in-a-strapless-red-dress-out-in-nyc-3229225.html",
    "#category": ("", "pictoa", "album"),
    "#class"   : pictoa.PictoaAlbumExtractor,
    "#pattern" : r"https://?(?:[\w]+\.)?pictoa\.com/albums/[\w-]+/[\d]+.html",
    "#count"   : 16,
    "album_id" : "3229225",
    "date"     : None,
    "title"    : "Anna Kendrick busty in a strapless red dress out in NYC",
    "tags"     : ["Anna Kendrick", "Celebrity"]
},
{
    # verify pagination works
    "#url"     : "https://www.pictoa.com/albums/oscars-2020-red-carpet-4010403.html",
    "#category": ("", "pictoa", "album"),
    "#class"   : pictoa.PictoaAlbumExtractor,
    "#pattern" : r"https://?(?:[\w]+\.)?pictoa\.com/albums/[\w-]+/[\d]+.html",
    "#count"   : 182,
    "album_id" : "4010403",
    "date"     : None,
    "title"    : "Oscars 2020 Red Carpet",
    "tags"     : ['Celebrity', 'Red']
},
{
    # null tags
    "#url"     : "https://www.pictoa.com/albums/carl-virkus-149024.html",
    "#category": ("", "pictoa", "album"),
    "#class"   : pictoa.PictoaAlbumExtractor,
    "#count"   : 1,
    "album_id" : "149024",
    "tags"     : []
},
{
    "#url"     : "https://www.pictoa.com/albums/anna-kendrick-showing-cleavage-at-the-56th-annual-grammy-awards-3233172/75206264.html",
    "#category": ("", "pictoa", "image"),
    "#class"   : pictoa.PictoaImageExtractor,
    "#pattern" : r"https://s1.pictoa.com/media/galleries/168/930/[\w\d]+/[\w\d]+.jpg",
    "id"       : "75206264",
},
)
