# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import picarto


__tests__ = (
{
    "#url"     : "https://picarto.tv/fnook/gallery/default/",
    "#category": ("", "picarto", "gallery"),
    "#class"   : picarto.PicartoGalleryExtractor,
    "#pattern" : r"https://images\.picarto\.tv/gallery/\d/\d\d/\d+/artwork/[0-9a-f-]+/large-[0-9a-f]+\.(jpg|png|gif)",
    "#count"   : ">= 7",

    "date": "type:datetime",
},

)
