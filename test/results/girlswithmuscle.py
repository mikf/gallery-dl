# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import girlswithmuscle


__tests__ = (
{
    "#url"     : "https://www.girlswithmuscle.com/2526619/",
    "#category": ("", "girlswithmuscle", "post"),
    "#class"   : girlswithmuscle.GirlswithmusclePostExtractor,
    "#results" : "https://www.girlswithmuscle.com/images/full/2526619.jpg",

    "comments" : [],
    "date"     : "dt:2025-05-21 20:01:03",
    "extension": "jpg",
    "filename" : "2526619",
    "id"       : "2526619",
    "is_favorite": None,
    "model"    : "Vladislava Galagan",
    "model_list" : [
        "Vladislava Galagan"
    ],
    "score"    : range(190, 250),
    "source_filename": "",
    "type"     : "picture",
    "uploader" : "mrt",
    "tags": [
        "delts/shoulders",
        "abs",
        "casual",
        "triceps",
        "traps",
        "bikini/competition suit",
        "white",
        "figure/fitness",
        "bodybuilder",
        "slavic",
        "women's physique",
        "russian",
    ],
},

{
    "#url"     : "https://www.girlswithmuscle.com/images/?name=Harmony%20Doughty",
    "#category": ("", "girlswithmuscle", "search"),
    "#class"   : girlswithmuscle.GirlswithmuscleSearchExtractor,
    "#pattern" : girlswithmuscle.GirlswithmusclePostExtractor.pattern,
    "#count"   : range(130, 150),
},

)
