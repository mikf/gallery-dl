# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagepond


__tests__ = (
{
    "#url"     : "https://www.imagepond.net/i/chv_317512",
    "#category": ("chevereto", "imagepond", "file"),
    "#class"   : imagepond.ImagepondFileExtractor,
    "#results" : "https://media.imagepond.net/media/IMG_20250217_1606226b345a5dbd0e8971.jpg",

    "album"    : "",
    "album_id" : "",
    "date"     : "dt:2025-02-17 00:00:00",
    "extension": "jpg",
    "filename" : "IMG_20250217_1606226b345a5dbd0e8971",
    "height"   : 976,
    "id"       : "chv_317512",
    "mime"     : "image/jpg",
    "title"    : "IMG_20250217_160622.jpg",
    "type"     : "image",
    "url"      : "https://media.imagepond.net/media/IMG_20250217_1606226b345a5dbd0e8971.jpg",
    "user"     : "dariusbbb24",
    "width"    : 720,
},

{
    "#url"     : "https://imagepond.net/image/IMG-20250217-160622.TJNphg",
    "#category": ("chevereto", "imagepond", "file"),
    "#class"   : imagepond.ImagepondFileExtractor,
    "#results"     : "https://media.imagepond.net/media/IMG_20250217_1606226b345a5dbd0e8971.jpg",
    "#sha1_content": "ec7fac6b427f7af01038619208cd69478e91ddef",

    "album"    : "",
    "date"     : "dt:2025-02-17 00:00:00",
    "extension": "jpg",
    "filename" : "IMG_20250217_1606226b345a5dbd0e8971",
    "id"       : "chv_317512",
    "mime"     : "image/jpg",
    "title"    : "IMG_20250217_160622.jpg",
    "type"     : "image",
    "url"      : "https://media.imagepond.net/media/IMG_20250217_1606226b345a5dbd0e8971.jpg",
    "user"     : "dariusbbb24",
},

{
    "#url"     : "https://www.imagepond.net/image/IMG-20250217-160622.TJNphg",
    "#category": ("chevereto", "imagepond", "file"),
    "#class"   : imagepond.ImagepondFileExtractor,
},

{
    "#url"     : "https://imagepond.net/video/1000423939.zb8Fxy",
    "#category": ("chevereto", "imagepond", "file"),
    "#class"   : imagepond.ImagepondFileExtractor,
    "#results" : "https://media.imagepond.net/media/100042393993a6bfa75fc505e9.mp4",

    "album"    : "",
    "album_id" : "",
    "date"     : "dt:2025-08-29 00:00:00",
    "duration" : 7,
    "extension": "mp4",
    "filename" : "100042393993a6bfa75fc505e9",
    "height"   : 1280,
    "id"       : "chv_787880",
    "thumbnail": "https://media.imagepond.net/media/./100042393993a6bfa75fc505e9_thumb.jpg",
    "title"    : "1000423939.mp4",
    "type"     : "video",
    "url"      : "https://media.imagepond.net/media/100042393993a6bfa75fc505e9.mp4",
    "user"     : "christiankita",
    "width"    : 720,
},

{
    "#url"     : "https://www.imagepond.net/a/chv_2822",
    "#category": ("chevereto", "imagepond", "album"),
    "#class"   : imagepond.ImagepondAlbumExtractor,
    "#pattern" : imagepond.ImagepondFileExtractor.pattern,
    "#count"   : 86,

    "album": "Aline Torres",
    "count": 86,
    "num"  : range(1, 86),
},

{
    "#url"     : "https://imagepond.net/album/CDilP/?sort=date_desc&page=1",
    "#category": ("chevereto", "imagepond", "album"),
    "#class"   : imagepond.ImagepondAlbumExtractor,
},

{
    "#url"     : "https://imagepond.net/dariusbbb24",
    "#category": ("chevereto", "imagepond", "user"),
    "#class"   : imagepond.ImagepondUserExtractor,
    "#auth"    : "cookies",
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://imagepond.net/ap000",
    "#comment" : "username starting with 'a' (#8149)",
    "#category": ("chevereto", "imagepond", "user"),
    "#class"   : imagepond.ImagepondUserExtractor,
    "#auth"    : "cookies",
},

)
