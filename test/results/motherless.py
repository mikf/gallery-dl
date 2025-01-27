# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import motherless


__tests__ = (
{
    "#url"  : "https://motherless.com/B0168DB",
    "#class": motherless.MotherlessMediaExtractor,
    "#urls" : "https://cdn5-images.motherlessmedia.com/images/B0168DB.jpg",
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
    "#url"  : "https://motherless.com/G43D8704/F0C07D3",
    "#class": motherless.MotherlessMediaExtractor,
    "#urls" : "https://cdn5-images.motherlessmedia.com/images/F0C07D3.jpg",

    "date"      : "dt:2014-08-13 00:00:00",
    "extension" : "jpg",
    "favorites" : range(100, 200),
    "filename"  : "F0C07D3",
    "gallery_id": "43D8704",
    "gallery_title": "SpeechLess",
    "group"     : "",
    "id"        : "F0C07D3",
    "tags"      : [],
    "title"     : "Spunky Angels Amy Black Dress",
    "type"      : "image",
    "uploader"  : "jonesyjonesy",
    "url"       : "https://cdn5-images.motherlessmedia.com/images/F0C07D3.jpg",
    "views"     : range(14000, 20000),
},

{
    "#url"  : "https://motherless.com/g/classic_porn/19D6C80",
    "#class": motherless.MotherlessMediaExtractor,
    "#urls" : "https://cdn5-images.motherlessmedia.com/images/19D6C80.gif",

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
    "#url"  : "https://motherless.com/G43D8704",
    "#class": motherless.MotherlessGalleryExtractor,
    "#urls": (
        "https://motherless.com/GI43D8704",
        "https://motherless.com/GV43D8704",
    ),
},

{
    "#url"  : "https://motherless.com/GI43D8704",
    "#class": motherless.MotherlessGalleryExtractor,
    "#pattern": r"https://cdn5-images\.motherlessmedia\.com/images/\w+\.(jpg|png|gif)",
    "#range"  : "1-100",
    "#count"  : 100,

    "count"        : range(5000, 8000),
    "extension"    : {"jpg", "png", "gif"},
    "filename"     : str,
    "gallery_id"   : "43D8704",
    "gallery_title": "SpeechLess",
    "id"           : str,
    "num"          : int,
    "thumbnail"    : r"re:https://cdn5-thumbs\.motherlessmedia\.com/thumbs/\w+\.\w+",
    "title"        : str,
    "type"         : "image",
    "uploader"     : "gaylobe",
    "url"          : r"re:https://cdn5-images\.motherlessmedia\.com/images/\w+\.(jpg|png|gif)",
},

{
    "#url"  : "https://motherless.com/GV43D8704",
    "#class": motherless.MotherlessGalleryExtractor,
    "#pattern": r"https://cdn5-videos.motherlessmedia.com/videos/\w+\.mp4",
    "#range"  : "1-100",
    "#count"  : 100,

    "count"        : range(500, 900),
    "extension"    : "mp4",
    "filename"     : str,
    "gallery_id"   : "43D8704",
    "gallery_title": "SpeechLess",
    "id"           : str,
    "num"          : int,
    "thumbnail"    : r"re:https://cdn5-thumbs\.motherlessmedia\.com/thumbs/[\w-]+\.\w+",
    "title"        : str,
    "type"         : "video",
    "uploader"     : "gaylobe",
    "url"          : r"re:https://cdn5-videos.motherlessmedia.com/videos/\w+\.mp4",
},

)
