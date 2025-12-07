# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import chevereto


__tests__ = (
{
    "#url"     : "https://imagepond.net/image/IMG-20250217-160622.TJNphg",
    "#category": ("chevereto", "imagepond", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#results"     : "https://media.imagepond.net/media/IMG_20250217_1606226b345a5dbd0e8971.jpg",
    "#sha1_content": "ec7fac6b427f7af01038619208cd69478e91ddef",

    "album"    : "",
    "date"     : "dt:2025-02-17 19:15:25",
    "extension": "jpg",
    "filename" : "IMG_20250217_1606226b345a5dbd0e8971",
    "id"       : "TJNphg",
    "url"      : "https://media.imagepond.net/media/IMG_20250217_1606226b345a5dbd0e8971.jpg",
    "user"     : "dariusbbb24",
},

{
    "#url"     : "https://www.imagepond.net/image/IMG-20250217-160622.TJNphg",
    "#category": ("chevereto", "imagepond", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://imagepond.net/video/1000423939.zb8Fxy",
    "#category": ("chevereto", "imagepond", "video"),
    "#class"   : chevereto.CheveretoVideoExtractor,
    "#results" : "https://media.imagepond.net/media/100042393993a6bfa75fc505e9.mp4",

    "album"    : "",
    "album_id" : "",
    "album_slug": "",
    "date"     : "dt:2025-08-29 18:01:20",
    "duration" : 7,
    "extension": "mp4",
    "filename" : "100042393993a6bfa75fc505e9",
    "height"   : 1280,
    "id"       : "zb8Fxy",
    "thumbnail": "https://media.imagepond.net/media/100042393993a6bfa75fc505e9.fr.jpeg",
    "title"    : "1000423939",
    "url"      : "https://media.imagepond.net/media/100042393993a6bfa75fc505e9.mp4",
    "user"     : "christiankita",
    "width"    : 720,
},

{
    "#url"     : "https://imagepond.net/album/CDilP/?sort=date_desc&page=1",
    "#category": ("chevereto", "imagepond", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
},

{
    "#url"     : "https://imagepond.net/dariusbbb24",
    "#category": ("chevereto", "imagepond", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://imagepond.net/ap000",
    "#comment" : "username starting with 'a' (#8149)",
    "#category": ("chevereto", "imagepond", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

)
