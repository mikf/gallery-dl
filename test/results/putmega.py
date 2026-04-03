# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import chevereto


__tests__ = (
{
    "#url"     : "https://putmega.com/image/IMG-8142c11f788cd53bdfde.v9sdX7",
    "#category": ("chevereto", "putmega", "file"),
    "#class"   : chevereto.CheveretoFileExtractor,
    "#results" : "https://putmega.com/images/IMG_8142c11f788cd53bdfde.jpeg",

    "album"     : "",
    "album_id"  : "",
    "album_slug": "",
    "date"      : "dt:2024-04-16 18:39:34",
    "extension" : "jpeg",
    "filename"  : "IMG_8142c11f788cd53bdfde",
    "id"        : "v9sdX7",
    "title"     : "IMG 8142c11f788cd53bdfde",
    "type"      : "article",
    "url"       : "https://putmega.com/images/IMG_8142c11f788cd53bdfde.jpeg",
    "user"      : "simpcity",
},

{
    "#url"     : "https://www.putmega.com/image/7e400e83004d18f17c32e13895af0877-xlargec71f5575edee84c0.BYSyt8",
    "#category": ("chevereto", "putmega", "file"),
    "#class"   : chevereto.CheveretoFileExtractor,
    "#results" : "https://putmega.com/images/7e400e83004d18f17c32e13895af0877-xlargec71f5575edee84c0.jpeg",

    "album"     : "scarlettkissesxo",
    "album_id"  : "",
    "album_slug": "",
    "date"      : "dt:2025-05-08 17:04:25",
    "extension" : "jpeg",
    "filename"  : "7e400e83004d18f17c32e13895af0877-xlargec71f5575edee84c0",
    "id"        : "BYSyt8",
    "title"     : "7e400e83004d18f17c32e13895af0877 xlargec71f5575edee84c0",
    "type"      : "article",
    "url"       : "https://putmega.com/images/7e400e83004d18f17c32e13895af0877-xlargec71f5575edee84c0.jpeg",
    "user"      : "simpcity",
},

{
    "#url"     : "https://www.putmega.com/album/scarlettkissesxo.SHiaN",
    "#category": ("chevereto", "putmega", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#pattern" : chevereto.CheveretoFileExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,

    "album"     : "scarlettkissesxo",
    "album_id"  : "SHiaN",
    "album_slug": "scarlettkissesxo",
    "count"     : 720,
    "num"       : range(1, 50),
},

{
    "#url"     : "https://www.putmega.com/simpcity",
    "#category": ("chevereto", "putmega", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

{
    "#url"     : "https://putme.ga/giraffegoat63",
    "#category": ("chevereto", "putmega", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

)
