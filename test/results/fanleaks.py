# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fanleaks
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://fanleaks.club/selti/880",
    "#category": ("", "fanleaks", "post"),
    "#class"   : fanleaks.FanleaksPostExtractor,
    "#pattern" : r"https://fanleaks\.club//models/selti/images/selti_0880\.jpg",

    "model_id": "selti",
    "model"   : "Selti",
    "id"      : 880,
    "type"    : "photo",
},

{
    "#url"     : "https://fanleaks.club/daisy-keech/1038",
    "#category": ("", "fanleaks", "post"),
    "#class"   : fanleaks.FanleaksPostExtractor,
    "#pattern" : r"https://fanleaks\.club//models/daisy-keech/videos/daisy-keech_1038\.mp4",

    "model_id": "daisy-keech",
    "model"   : "Daisy Keech",
    "id"      : 1038,
    "type"    : "video",
},

{
    "#url"     : "https://fanleaks.club/hannahowo/000",
    "#category": ("", "fanleaks", "post"),
    "#class"   : fanleaks.FanleaksPostExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://fanleaks.club/hannahowo",
    "#category": ("", "fanleaks", "model"),
    "#class"   : fanleaks.FanleaksModelExtractor,
    "#pattern" : r"https://fanleaks\.club//models/hannahowo/(images|videos)/hannahowo_\d+\.\w+",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://fanleaks.club/belle-delphine",
    "#category": ("", "fanleaks", "model"),
    "#class"   : fanleaks.FanleaksModelExtractor,
    "#pattern" : r"https://fanleaks\.club//models/belle-delphine/(images|videos)/belle-delphine_\d+\.\w+",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://fanleaks.club/daisy-keech",
    "#category": ("", "fanleaks", "model"),
    "#class"   : fanleaks.FanleaksModelExtractor,
},

)
