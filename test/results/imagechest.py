# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagechest
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://imgchest.com/p/3na7kr3by8d",
    "#category": ("", "imagechest", "gallery"),
    "#class"   : imagechest.ImagechestGalleryExtractor,
    "#pattern"     : r"https://cdn\.imgchest\.com/files/\w+\.(jpg|png)",
    "#count"       : 3,
    "#sha1_url"    : "7328ca4ec2459378d725e3be19f661d2b045feda",
    "#sha1_content": "076959e65be30249a2c651fbe6090dc30ba85193",

    "count"     : 3,
    "gallery_id": "3na7kr3by8d",
    "num"       : int,
    "title"     : "Wizardry - Video Game From The Mid 80's",
},

{
    "#url"     : "https://imgchest.com/p/9p4n3q2z7nq",
    "#comment" : "'Load More Files' button (#4028)",
    "#category": ("", "imagechest", "gallery"),
    "#class"   : imagechest.ImagechestGalleryExtractor,
    "#pattern" : r"https://cdn\.imgchest\.com/files/\w+\.(jpg|png)",
    "#count"   : 52,
    "#sha1_url": "f5674e8ba79d336193c9f698708d9dcc10e78cc7",
},

{
    "#url"     : "https://imgchest.com/p/xxxxxxxxxxx",
    "#category": ("", "imagechest", "gallery"),
    "#class"   : imagechest.ImagechestGalleryExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://imgchest.com/u/LunarLandr",
    "#category": ("", "imagechest", "user"),
    "#class"   : imagechest.ImagechestUserExtractor,
    "#pattern" : imagechest.ImagechestGalleryExtractor.pattern,
    "#count"   : range(280, 290),
},

)
