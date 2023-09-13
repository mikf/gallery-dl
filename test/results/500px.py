# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.500px")
_500px = getattr(gallery_dl.extractor, "500px")


__tests__ = (
{
    "#url"     : "https://500px.com/p/light_expression_photography",
    "#category": ("", "500px", "user"),
    "#class"   : _500px._500pxUserExtractor,
    "#pattern" : r"https?://drscdn.500px.org/photo/\d+/m%3D4096/v2",
    "#range"   : "1-99",
    "#count"   : 99,
},

{
    "#url"     : "https://500px.com/light_expression_photography",
    "#category": ("", "500px", "user"),
    "#class"   : _500px._500pxUserExtractor,
},

{
    "#url"     : "https://web.500px.com/light_expression_photography",
    "#category": ("", "500px", "user"),
    "#class"   : _500px._500pxUserExtractor,
},

{
    "#url"     : "https://500px.com/p/fashvamp/galleries/lera",
    "#category": ("", "500px", "gallery"),
    "#class"   : _500px._500pxGalleryExtractor,
    "#count"   : 3,
    "#sha1_url": "002dc81dee5b4a655f0e31ad8349e8903b296df6",

    "gallery": dict,
    "user"   : dict,
},

{
    "#url"     : "https://500px.com/fashvamp/galleries/lera",
    "#category": ("", "500px", "gallery"),
    "#class"   : _500px._500pxGalleryExtractor,
},

{
    "#url"     : "https://500px.com/liked",
    "#category": ("", "500px", "favorite"),
    "#class"   : _500px._500pxFavoriteExtractor,
},

{
    "#url"     : "https://500px.com/photo/222049255/queen-of-coasts",
    "#category": ("", "500px", "image"),
    "#class"   : _500px._500pxImageExtractor,
    "#count"   : 1,
    "#sha1_url": "fbdf7df39325cae02f5688e9f92935b0e7113315",

    "camera"          : "Canon EOS 600D",
    "camera_info"     : dict,
    "comments"        : list,
    "comments_count"  : int,
    "created_at"      : "2017-08-01T08:40:05+00:00",
    "description"     : str,
    "editored_by"     : None,
    "editors_choice"  : False,
    "extension"       : "jpg",
    "feature"         : "popular",
    "feature_date"    : "2017-08-01T09:58:28+00:00",
    "focal_length"    : "208",
    "height"          : 3111,
    "id"              : 222049255,
    "image_format"    : "jpg",
    "image_url"       : list,
    "images"          : list,
    "iso"             : "100",
    "lens"            : "EF-S55-250mm f/4-5.6 IS II",
    "lens_info"       : dict,
    "liked"           : None,
    "location"        : None,
    "location_details": dict,
    "name"            : "Queen Of Coasts",
    "nsfw"            : False,
    "privacy"         : False,
    "profile"         : True,
    "rating"          : float,
    "status"          : 1,
    "tags"            : list,
    "taken_at"        : "2017-05-04T17:36:51+00:00",
    "times_viewed"    : int,
    "url"             : "/photo/222049255/Queen-Of-Coasts-by-Alice-Nabieva",
    "user"            : dict,
    "user_id"         : 12847235,
    "votes_count"     : int,
    "watermark"       : True,
    "width"           : 4637,
},

)
