# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import redbust


__tests__ = (
{
    "#url"     : "https://redbust.com/sadie-gray-wearing-black-nighty/",
    "#class"   : redbust.RedbustGalleryExtractor,
    "#pattern" : r"https://redbust.com/stuff/sadie-gray-wearing-black-nighty/sadie-gray-morning-ritual-bathroom-naked-boobs-nighty-playboy-\d+\.jpg",
    "#count"   : 35,

    "count"       : 35,
    "num"         : range(1, 35),
    "date"        : "dt:2024-03-19 00:00:00",
    "extension"   : "jpg",
    "filename"    : str,
    "gallery_id"  : "373920",
    "gallery_slug": "sadie-gray-wearing-black-nighty",
    "title"       : "Sadie Gray wearing black nighty",
    "views"       : range(38_000, 50_000),
    "categories": [
        "Super Chicks",
    ],
    "tags"        : [
        "bathroom",
        "nighty",
        "playboy",
        "redhead",
        "sadie gray",
    ],
},

{
    "#url"     : "https://redbust.com/girls-in-carwash/",
    "#comment" : "legacy",
    "#class"   : redbust.RedbustGalleryExtractor,
    "#pattern" : r"https://redbust.com/wp-content/uploads/girls_in_carwash/girls_in_carwash_\d+\.jpg",
    "#count"   : 27,

    "count"       : 27,
    "num"         : range(1, 27),
    "date"        : "dt:2010-09-05 00:00:00",
    "extension"   : "jpg",
    "filename"    : str,
    "gallery_id"  : "6517",
    "gallery_slug": "girls-in-carwash",
    "title"       : "Girls in carwash",
    "views"       : range(9_000, 20_000),
    "categories": [
        "Automotive",
    ],
    "tags"        : [
        "carwash",
    ],
},

{
    "#url"     : "https://redbust.com/other/",
    "#comment" : "'category' listing",
    "#class"   : redbust.RedbustGalleryExtractor,
    "#pattern" : redbust.RedbustGalleryExtractor.pattern,
    "#count"   : 28,
},

)
