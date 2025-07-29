# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikifeet


__tests__ = (
{
    "#url"     : "https://www.wikifeetx.com/Tifa_Quinn",
    "#category": ("", "wikifeetx", "gallery"),
    "#class"   : wikifeet.WikifeetGalleryExtractor,
    "#pattern" : r"https://pics\.wikifeet\.com/Tifa_Quinn-Feet-\d+\.jpg",
    "#count"   : ">= 9",

    "celeb"     : "Tifa_Quinn",
    "celebrity" : "Tifa Quinn",
    "birthday"  : "",
    "birthplace": "United States",
    "rating"    : float,
    "pid"       : int,
    "width"     : int,
    "height"    : int,
    "shoesize"  : "5",
    "type"      : "women",
    "tags"      : list,
},

)
