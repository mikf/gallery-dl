# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikifeet


__tests__ = (
{
    "#url"     : "https://www.wikifeet.com/Madison_Beer",
    "#category": ("", "wikifeet", "gallery"),
    "#class"   : wikifeet.WikifeetGalleryExtractor,
    "#pattern" : r"https://pics\.wikifeet\.com/Madison_Beer-Feet-\d+\.jpg",
    "#count"   : ">= 352",

    "celeb"     : "Madison_Beer",
    "celebrity" : "Madison Beer",
    "birthday"  : "dt:1999-03-05 00:00:00",
    "birthplace": "United States",
    "rating"    : float,
    "pid"       : int,
    "width"     : int,
    "height"    : int,
    "shoesize"  : "9 US",
    "type"      : "women",
    "tags"      : list,
},

{
    "#url"     : "https://men.wikifeet.com/Chris_Hemsworth",
    "#category": ("", "wikifeet", "gallery"),
    "#class"   : wikifeet.WikifeetGalleryExtractor,
    "#pattern" : r"https://pics\.wikifeet\.com/Chris_Hemsworth-Feet-\d+\.jpg",
    "#count"   : ">= 860",

    "celeb"     : "Chris_Hemsworth",
    "celebrity" : "Chris Hemsworth",
    "birthday"  : "dt:1983-08-11 00:00:00",
    "birthplace": "Australia",
    "rating"    : float,
    "pid"       : int,
    "width"     : int,
    "height"    : int,
    "shoesize"  : "12.5 US",
    "type"      : "men",
    "tags"      : list,
},

)
