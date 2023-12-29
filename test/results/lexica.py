# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lexica


__tests__ = (
{
    "#url"     : "https://lexica.art/?q=tree",
    "#category": ("", "lexica", "search"),
    "#class"   : lexica.LexicaSearchExtractor,
    "#pattern" : r"https://lexica-serve-encoded-images2\.sharif\.workers.dev/full_jpg/[0-9a-f-]{36}$",
    "#range"   : "1-80",
    "#count"   : 80,

    "height"         : int,
    "id"             : str,
    "upscaled_height": int,
    "upscaled_width" : int,
    "userid"         : str,
    "width"          : int,
    "prompt"         : {
        "c"                : int,
        "grid"             : bool,
        "height"           : int,
        "id"               : str,
        "images"           : list,
        "initImage"        : None,
        "initImageStrength": None,
        "model"            : "lexica-aperture-v2",
        "negativePrompt"   : str,
        "prompt"           : str,
        "seed"             : str,
        "timestamp"        : r"re:\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\dZ",
        "width"            : int,
    },
},

)
