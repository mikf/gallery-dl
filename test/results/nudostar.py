# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nudostar


__tests__ = (
{
    "#url"    : "https://nudostar.tv/models/eva-joys/",
    "#class"  : nudostar.NudostarModelExtractor,
    "#pattern": r"https://nudostar.tv/contents/e/v/eva-joys/1000/eva-joys_\d{4}\.jpg",
    "#count"  : range(50, 80),

    "count"      : 54,
    "num"        : range(1, 54),
    "extension"  : "jpg",
    "filename"   : r"re:eva-joys_00\d\d",
    "gallery_id" : "eva-joys",
    "model"      : "eva_joy",
    "model_slug" : "eva-joys",
    "model_names": [
        "eva_joy",
        "eva_joys",
    ],
},

{
    "#url"    : "https://nl.nudostar.tv/models/eva-joys/",
    "#class"  : nudostar.NudostarModelExtractor,
},

{
    "#url"    : "https://nudostar.tv/models/thebigtittiecommittee/148/",
    "#class"  : nudostar.NudostarImageExtractor,
    "#results": "https://nudostar.tv/contents/t/h/thebigtittiecommittee/1000/thebigtittiecommittee_0148.jpg",

    "extension"  : "jpg",
    "filename"   : "thebigtittiecommittee_0148",
    "gallery_id" : "thebigtittiecommittee",
    "num"        : 148,
    "url"        : "https://nudostar.tv/contents/t/h/thebigtittiecommittee/1000/thebigtittiecommittee_0148.jpg",
    "model"      : "Hari Beavis",
    "model_slug" : "thebigtittiecommittee",
    "model_names": [
        "Hari Beavis",
        "Thebigtittiecommittee",
    ],
},

)
