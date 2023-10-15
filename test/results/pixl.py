# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import chevereto


__tests__ = (
{
    "#url"     : "https://pixl.li/image/894x1023-1c8d6dd3b1b0cd4b0d286b229157a7de.z3DwHB",
    "#category": ("chevereto", "pixl", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#urls"        : "https://i.pixl.li/894x1023_1c8d6dd3b1b0cd4b0d286b229157a7de.jpg",
    "#sha1_content": "3279b86d0ac42348c703770c4781ecdc300fc13c",

    "album": "",
    "extension": "jpg",
    "filename": "894x1023_1c8d6dd3b1b0cd4b0d286b229157a7de",
    "id": "z3DwHB",
    "url": "https://i.pixl.li/894x1023_1c8d6dd3b1b0cd4b0d286b229157a7de.jpg",
    "user": "matafaka1",
},

{
    "#url"     : "https://pixl.is/image/894x1023-1c8d6dd3b1b0cd4b0d286b229157a7de.z3DwHB",
    "#category": ("chevereto", "pixl", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://pixl.li/album/estelasaubi.D0bJf",
    "#category": ("chevereto", "pixl", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#pattern" : chevereto.CheveretoImageExtractor.pattern,
    "#count"   : 173,
},

{
    "#url"     : "https://pixl.li/mjstik",
    "#category": ("chevereto", "pixl", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#pattern" : chevereto.CheveretoImageExtractor.pattern,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://pixl.li/mjstik/albums",
    "#category": ("chevereto", "pixl", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#pattern" : chevereto.CheveretoAlbumExtractor.pattern,
    "#count"   : 285,
},

{
    "#url"     : "https://pixl.is/renford/albums",
    "#category": ("chevereto", "pixl", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

)
