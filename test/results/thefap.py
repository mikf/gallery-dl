# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import thefap


__tests__ = (
{
    "#url"     : "https://thefap.net/zoey.curly-374261/xpics/i8",
    "#class"   : thefap.ThefapPostExtractor,
    "#results" : "https://cdn31.xpics.me/photo/2024/10/01/09/CR98EY1fSquX.jpg",

    "extension" : "jpg",
    "filename"  : "CR98EY1fSquX",
    "kind"      : "xpics",
    "model"     : "zoey.curly",
    "model_id"  : 374261,
    "model_name": "Zoey Curly",
    "num"       : 1,
    "post_id"   : 8,
},

{
    "#url"     : "https://thefap.net/analovesbananaas-979268/fap-onlyfans-0-1qcckka/i2",
    "#class"   : thefap.ThefapPostExtractor,
    "#results" : "https://i0.wp.com/i.redd.it/b4o1olbgi8dg1.jpg",

    "extension" : "jpg",
    "kind"      : "fap-onlyfans-0-1qcckka",
    "model"     : "analovesbananaas",
    "model_id"  : 979268,
    "model_name": "analovesbananaas",
    "num"       : 1,
    "post_id"   : 2,
},

{
    "#url"     : "https://thefap.net/tatted-mamma-979518/twpornstars/i1",
    "#class"   : thefap.ThefapPostExtractor,
    "#results" : "https://pbs.twimg.com/media/GFmqJn2a8AAAtKu.jpg:orig",

    "extension" : "jpg:orig",
    "filename"  : "GFmqJn2a8AAAtKu",
    "kind"      : "twpornstars",
    "model"     : "tatted-mamma",
    "model_id"  : 979518,
    "model_name": "tatted_mamma",
    "num"       : 1,
    "post_id"   : 1,
},

{
    "#url"     : "https://thefap.net/zoey.curly-374261/",
    "#class"   : thefap.ThefapModelExtractor,
    "#range"   : "1-100",
    "#count"   : 100,

    "extension" : "jpg",
    "filename"  : str,
    "model"     : "zoey.curly",
    "model_id"  : 374261,
    "model_name": "Zoey Curly",
    "num"       : range(1, 100),
},

{
    "#url"     : "https://thefap.net/analovesbananaas-979268/",
    "#class"   : thefap.ThefapModelExtractor,
    "#results" : (
        "https://i0.wp.com/i.redd.it/icndsjbgi8dg1.jpg",
        "https://i0.wp.com/i.redd.it/b4o1olbgi8dg1.jpg",
        "https://i0.wp.com/i.redd.it/aqilnkbgi8dg1.jpg",
    ),

    "extension" : "jpg",
    "filename"  : str,
    "model"     : "analovesbananaas",
    "model_id"  : 979268,
    "model_name": "analovesbananaas",
    "num"       : range(1, 3),
},

)
