# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pictoa


__tests__ = (
{
    "#url"    : "https://www.pictoa.com/albums/anna-kendrick-busty-in-a-strapless-red-dress-out-in-nyc-3229225.html",
    "#class"  : pictoa.PictoaAlbumExtractor,
    "#pattern": pictoa.PictoaImageExtractor.pattern,
    "#count"  : 16,

    "album_id"   : "3229225",
    "album_title": "Anna Kendrick busty in a strapless red dress out in NYC",
    "tags"       : ["Anna Kendrick", "Celebrity"],
},

{
    "#url"    : "https://www.pictoa.com.de/albums/oscars-2020-red-carpet-4010403.html",
    "#comment": "verify pagination works",
    "#class"  : pictoa.PictoaAlbumExtractor,
    "#pattern": pictoa.PictoaImageExtractor.pattern,
    "#count"  : 182,

    "album_id"   : "4010403",
    "album_title": "Oscars 2020 Red Carpet",
    "tags"       : ['Celebrity', 'Red'],
},

{
    "#url"    : "https://it.pictoa.com/albums/carl-virkus-149024.html",
    "#comment": "null tags",
    "#class"  : pictoa.PictoaAlbumExtractor,
    "#results": "https://www.pictoa.com/albums/carl-virkus-149024/2221031.html",

    "album_id"   : "149024",
    "album_title": "Carl Virkus",
    "tags"       : [],
},

{
    "#url"  : "https://www.pictoa.com/albums/anna-kendrick-showing-cleavage-at-the-56th-annual-grammy-awards-3233172/75206264.html",
    "#class": pictoa.PictoaImageExtractor,
    "#results": "https://s1.pictoa.com/media/galleries/168/930/168930594a8750dfd3e/3233172594a8759dcc3a.jpg",

    "album_id"   : "3233172",
    "album_title": "Anna Kendrick showing cleavage at the 56th Annual GRAMMY Awards",
    "extension"  : "jpg",
    "filename"   : "3233172594a8759dcc3a",
    "id"         : "75206264",
    "url"        : "https://s1.pictoa.com/media/galleries/168/930/168930594a8750dfd3e/3233172594a8759dcc3a.jpg"
},

{
    "#url"  : "https://nl.pictoa.com/albums/kandi-barbour-3840809/94038192.html",
    "#class": pictoa.PictoaImageExtractor,
    "#results"     : "https://s2.pictoa.com/media/galleries/294/452/29445260009fa5b68e4/384080960009fb51e389.jpg",
    "#sha1_content": "152595069016da89565eb3d8e73df835afd22e2c",

    "album_id"   : "3840809",
    "album_title": "Kandi Barbour",
    "extension"  : "jpg",
    "filename"   : "384080960009fb51e389",
    "id"         : "94038192",
    "url"        : "https://s2.pictoa.com/media/galleries/294/452/29445260009fa5b68e4/384080960009fb51e389.jpg",
},

)
