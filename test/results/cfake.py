# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import cfake


__tests__ = (
{
    "#url"     : "https://cfake.com/images/celebrity/Kaley_Cuoco/631/",
    "#category": ("", "cfake", "celebrity"),
    "#class"   : cfake.CfakeCelebrityExtractor,
    "#pattern" : r"https://cfake\.com/medias/photos/\d{4}/[0-9a-f]+_cfake\.jpg",
    "#range"   : "1-20",
    "#count"   : 20,

    "type"         : "celebrity",
    "type_id"      : 631,
    "type_name"    : "Kaley Cuoco",
    "page"         : 1,
    "id"           : int,
    "num"          : int,
    "date"         : str,
    "rating"       : str,
},

{
    "#url"     : "https://cfake.com/images/celebrity/Kaley_Cuoco/631/p2",
    "#comment" : "pagination test - page 2",
    "#category": ("", "cfake", "celebrity"),
    "#class"   : cfake.CfakeCelebrityExtractor,
    "#pattern" : r"https://cfake\.com/medias/photos/\d{4}/[0-9a-f]+_cfake\.jpg",
    "#range"   : "1-5",

    "type"         : "celebrity",
    "type_id"      : 631,
    "type_name"    : "Kaley Cuoco",
    "page"         : 2,
},

{
    "#url"     : "https://www.cfake.com/images/celebrity/Chloe_Grace_Moretz/6575/",
    "#category": ("", "cfake", "celebrity"),
    "#class"   : cfake.CfakeCelebrityExtractor,
},

{
    "#url"     : "https://cfake.com/images/categories/Facial/25/",
    "#category": ("", "cfake", "category"),
    "#class"   : cfake.CfakeCategoryExtractor,
    "#pattern" : r"https://cfake\.com/medias/photos/\d{4}/[0-9a-f]+_cfake\.jpg",
    "#range"   : "1-10",
    "#count"   : 10,

    "type"        : "category",
    "type_id"     : 25,
    "type_name"   : "Facial",
    "page"        : 1,
    "id"          : int,
    "num"         : int,
},

{
    "#url"     : "https://cfake.com/images/categories/Big_Tits/35/",
    "#category": ("", "cfake", "category"),
    "#class"   : cfake.CfakeCategoryExtractor,
},

{
    "#url"     : "https://cfake.com/images/categories/Big_Tits/35/p2",
    "#comment" : "category pagination test",
    "#category": ("", "cfake", "category"),
    "#class"   : cfake.CfakeCategoryExtractor,
},

{
    "#url"     : "https://cfake.com/images/created/Spice_Girls_%28band%29/72/4",
    "#category": ("", "cfake", "created"),
    "#class"   : cfake.CfakeCreatedExtractor,
    "#pattern" : r"https://cfake\.com/medias/photos/\d{4}/[0-9a-f]+_cfake\.jpg",
    "#range"   : "1-10",
    "#count"   : 10,

    "type"       : "created",
    "type_id"    : 72,
    "type_name"  : "Spice Girls (band)",
    "sub_id"     : 4,
    "page"       : 1,
    "id"         : int,
    "num"        : int,
},

{
    "#url"     : "https://cfake.com/images/created/Brooklyn_Nine-Nine/4142/4",
    "#category": ("", "cfake", "created"),
    "#class"   : cfake.CfakeCreatedExtractor,
},

{
    "#url"     : "https://cfake.com/images/created/Brooklyn_Nine-Nine/4142/4/p2",
    "#comment" : "created pagination test",
    "#category": ("", "cfake", "created"),
    "#class"   : cfake.CfakeCreatedExtractor,
},

{
    "#url"     : "https://cfake.com/images/country/Australia/12/5",
    "#category": ("", "cfake", "country"),
    "#class"   : cfake.CfakeCountryExtractor,
    "#pattern" : r"https://cfake\.com/medias/photos/\d{4}/[0-9a-f]+_cfake\.jpg",
    "#range"   : "1-10",
    "#count"   : 10,

    "type"       : "country",
    "type_id"    : 12,
    "type_name"  : "Australia",
    "sub_id"     : 5,
    "page"       : 1,
    "id"         : int,
    "num"        : int,
},

{
    "#url"     : "https://cfake.com/images/country/Mexico/139/5",
    "#category": ("", "cfake", "country"),
    "#class"   : cfake.CfakeCountryExtractor,
},

{
    "#url"     : "https://cfake.com/images/country/Mexico/139/5/p3",
    "#comment" : "country pagination test",
    "#category": ("", "cfake", "country"),
    "#class"   : cfake.CfakeCountryExtractor,
},

)
