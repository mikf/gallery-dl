# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import motherless
from gallery_dl import exception


__tests__ = (
{
    "#url"  : "https://motherless.com/B0168DB",
    "#class": motherless.MotherlessMediaExtractor,
    "#results": "https://cdn5-images.motherlessmedia.com/images/B0168DB.jpg",
    "#sha1_content": "10629fc5dd7a9623af7dd57f1a322d0f24ac9acc",

    "date"     : "dt:2013-03-29 00:00:00",
    "extension": "jpg",
    "favorites": range(0, 10),
    "filename" : "B0168DB",
    "group"    : "",
    "id"       : "B0168DB",
    "tags"     : [
        "Lady J",
        "outdoor",
        "closeup. face"
    ],
    "title"    : "388652199_d6fc8a9515_o.jpg",
    "type"     : "image",
    "uploader" : "anonymous",
    "url"      : "https://cdn5-images.motherlessmedia.com/images/B0168DB.jpg",
    "views"    : range(90, 200),

},

{
    "#url"  : "https://motherless.com/g/classic_porn/19D6C80",
    "#class": motherless.MotherlessMediaExtractor,
    "#results": "https://cdn5-images.motherlessmedia.com/images/19D6C80.gif",

    "date"     : "dt:2021-05-11 00:00:00",
    "extension": "gif",
    "favorites": range(10, 50),
    "filename" : "19D6C80",
    "group"    : "classic_porn",
    "id"       : "19D6C80",
    "tags"     : [],
    "title"    : "Kaffee 1",
    "type"     : "image",
    "uploader" : "KurtRitter",
    "url"      : "https://cdn5-images.motherlessmedia.com/images/19D6C80.gif",
    "views"    : range(150000, 300000),
},

{
    "#url"  : "https://motherless.com/G444B6FA/46ABC1A",
    "#class": motherless.MotherlessMediaExtractor,
    "#results": "https://cdn5-images.motherlessmedia.com/images/46ABC1A.jpg",

    "date"      : "dt:2017-11-24 00:00:00",
    "extension" : "jpg",
    "favorites" : range(0, 100),
    "filename"  : "46ABC1A",
    "gallery_id": "444B6FA",
    "group"     : "",
    "id"        : "46ABC1A",
    "tags"      : [
        "rope",
        "bondage",
        "bdsm"
    ],
    "title"     : "Some More Pix",
    "type"      : "image",
    "uploader"  : "FATBOY114",
    "url"       : "https://cdn5-images.motherlessmedia.com/images/46ABC1A.jpg",
    "views"     : range(100, 2000),
},

{
    "#url"     : "https://motherless.com/8850983",
    "#class"   : motherless.MotherlessMediaExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"  : "https://motherless.com/G444B6FA",
    "#class": motherless.MotherlessGalleryExtractor,
    "#results": (
        "https://motherless.com/GI444B6FA",
        "https://motherless.com/GV444B6FA",
    ),
},

{
    "#url"  : "https://motherless.com/GI444B6FA",
    "#class": motherless.MotherlessGalleryExtractor,
    "#pattern": r"https://cdn5-images\.motherlessmedia\.com/images/[^/]+\.(jpg|jpeg|png|gif)",
    "#range"  : "1-100",
    "#count"  : range(5, 50),

    "count"        : range(5, 50),
    "extension"    : {"jpg", "jpeg", "png", "gif"},
    "filename"     : str,
    "gallery_id"   : "444B6FA",
    "id"           : str,
    "num"          : int,
    "thumbnail"    : r"re:https://cdn5-thumbs\.motherlessmedia\.com/thumbs/[^/]+\.\w+",
    "title"        : str,
    "type"         : "image",
    "uploader"     : "WawaWeWa",
    "url"          : r"re:https://cdn5-images\.motherlessmedia\.com/images/[^/]+\.(jpg|jpeg|png|gif)",
},

{
    "#url"  : "https://motherless.com/GV444B6FA",
    "#class": motherless.MotherlessGalleryExtractor,
    "#pattern": r"https://cdn5-videos\.motherlessmedia\.com/videos/[^/]+\.mp4(?:\?.*)?",
    "#range"  : "1-100",
    "#count"  : range(20, 40),

    "count"        : range(20, 100),
    "extension"    : "mp4",
    "filename"     : str,
    "gallery_id"   : "444B6FA",
    "id"           : str,
    "num"          : int,
    "thumbnail"    : r"re:https://cdn5-thumbs\.motherlessmedia\.com/thumbs/[^/]+\.\w+",
    "title"        : str,
    "type"         : "video",
    "uploader"     : "WawaWeWa",
    "url"          : r"re:https://cdn5-videos.motherlessmedia.com/videos/[^/]+\.mp4(?:\?.*)?",
},

{
    "#url"     : "https://motherless.com/GI466D59F",
    "#class"   : motherless.MotherlessGalleryExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"  : "https://motherless.com/g/bump___grind",
    "#class": motherless.MotherlessGroupExtractor,
    "#results": (
        "https://motherless.com/gi/bump___grind",
        "https://motherless.com/gv/bump___grind",
    ),
},

{
    "#url"  : "https://motherless.com/gi/bump___grind",
    "#class": motherless.MotherlessGroupExtractor,
    "#pattern": r"https://cdn5-images\.motherlessmedia\.com/images/[^/]+\.(jpg|jpeg|png|gif)",
    "#range"  : "1-100",
    "#count"  : 18,

    "count"        : range(5, 50),
    "extension"    : {"jpg", "jpeg", "png", "gif"},
    "filename"     : str,
    "group_id"     : "bump___grind",
    "group"        : "bump___grind",
    "id"           : str,
    "num"          : int,
    "thumbnail"    : r"re:https://cdn5-thumbs\.motherlessmedia\.com/thumbs/[^/]+\.\w+",
    "title"        : str,
    "type"         : "image",
    "url"          : r"re:https://cdn5-images\.motherlessmedia\.com/images/[^/]+\.(jpg|jpeg|png|gif)",
},

{
    "#url"  : "https://motherless.com/gv/bump___grind",
    "#class": motherless.MotherlessGroupExtractor,
    "#pattern": r"https://cdn5-videos\.motherlessmedia\.com/videos/[^/]+\.mp4(?:\?.*)?",
    "#range"  : "1-100",
    "#count"  : 25,

    "count"        : range(20, 100),
    "extension"    : "mp4",
    "filename"     : str,
    "group_id"     : "bump___grind",
    "group"        : "bump___grind",
    "id"           : str,
    "num"          : int,
    "thumbnail"    : r"re:https://cdn5-thumbs\.motherlessmedia\.com/thumbs/[^/]+\.\w+",
    "title"        : str,
    "type"         : "video",
    "url"          : r"re:https://cdn5-videos.motherlessmedia.com/videos/[^/]+\.mp4(?:\?.*)?",
},

)
