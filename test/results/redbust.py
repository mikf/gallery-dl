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
    "categories"  : [
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
    "categories"  : [
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

{
    "#url"     : "https://redbust.com/tag/tan-lines/",
    "#class"   : redbust.RedbustTagExtractor,
    "#pattern" : redbust.RedbustGalleryExtractor.pattern,
    "#count"   : range(70, 100),
},

{
    "#url"     : "https://redbust.com/2021/04/",
    "#class"   : redbust.RedbustArchiveExtractor,
    "#pattern" : redbust.RedbustGalleryExtractor.pattern,
    "#count"   : 25,
},

{
    "#url"     : "https://redbust.com/sadie-gray-wearing-black-nighty/sadie-gray-morning-ritual-bathroom-naked-boobs-nighty-playboy-04/",
    "#class"   : redbust.RedbustImageExtractor,
    "#results" : "https://redbust.com/stuff/sadie-gray-wearing-black-nighty/sadie-gray-morning-ritual-bathroom-naked-boobs-nighty-playboy-04.jpg",

    "count"       : 1,
    "num"         : 4,
    "extension"   : "jpg",
    "filename"    : "sadie-gray-morning-ritual-bathroom-naked-boobs-nighty-playboy-04",
    "gallery_slug": "sadie-gray-wearing-black-nighty",
    "image_id"    : "373925",
    "image_slug"  : "sadie-gray-morning-ritual-bathroom-naked-boobs-nighty-playboy-04",
    "title"       : "Sadie Gray wearing black nighty",
    "url"         : "https://redbust.com/stuff/sadie-gray-wearing-black-nighty/sadie-gray-morning-ritual-bathroom-naked-boobs-nighty-playboy-04.jpg",
},

)
