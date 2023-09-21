# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import architizer


__tests__ = (
{
    "#url"     : "https://architizer.com/projects/house-lo/",
    "#category": ("", "architizer", "project"),
    "#class"   : architizer.ArchitizerProjectExtractor,
    "#pattern" : r"https://architizer-prod\.imgix\.net/media/mediadata/uploads/.+\.jpg$",

    "count"      : 27,
    "description": str,
    "firm"       : "Atelier Lina Bellovicova",
    "gid"        : "225496",
    "location"   : "Czechia",
    "num"        : int,
    "size"       : "1000 sqft - 3000 sqft",
    "slug"       : "house-lo",
    "status"     : "Built",
    "subcategory": "project",
    "title"      : "House LO",
    "type"       : "Residential › Private House",
    "year"       : "2020",
},

{
    "#url"     : "https://architizer.com/firms/olson-kundig/",
    "#category": ("", "architizer", "firm"),
    "#class"   : architizer.ArchitizerFirmExtractor,
    "#pattern" : architizer.ArchitizerProjectExtractor.pattern,
    "#count"   : ">= 90",
},

)
