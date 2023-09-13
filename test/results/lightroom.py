# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lightroom


__tests__ = (
{
    "#url"     : "https://lightroom.adobe.com/shares/0c9cce2033f24d24975423fe616368bf",
    "#category": ("", "lightroom", "gallery"),
    "#class"   : lightroom.LightroomGalleryExtractor,
    "#count"   : ">= 55",

    "title": "Sterne und Nachtphotos",
    "user" : "Christian Schrang",
},

{
    "#url"     : "https://lightroom.adobe.com/shares/7ba68ad5a97e48608d2e6c57e6082813",
    "#category": ("", "lightroom", "gallery"),
    "#class"   : lightroom.LightroomGalleryExtractor,
    "#count"   : ">= 180",

    "title": "HEBFC Snr/Res v Brighton",
    "user" : "",
},

)
