# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import unsplash


__tests__ = (
{
    "#url"     : "https://unsplash.com/photos/lsoogGC_5dg",
    "#category": ("", "unsplash", "image"),
    "#class"   : unsplash.UnsplashImageExtractor,
    "#pattern" : r"https://images\.unsplash\.com/photo-1586348943529-beaae6c28db9\?ixid=\w+&ixlib=rb-4.0.3",

    "alt_description": r"re:silhouette of trees near body of water ",
    "blur_hash"      : "LZP4uQS4jboe%#o0WCa}2doJNaaz",
    "?  categories"  : list,
    "color"          : "#f3c08c",
    "created_at"     : "2020-04-08T12:29:42Z",
    "date"           : "dt:2020-04-08 12:29:42",
    "description"    : "The Island",
    "downloads"      : int,
    "exif"           : {
        "aperture"     : "11",
        "exposure_time": "30",
        "focal_length" : "70.0",
        "iso"          : 200,
        "make"         : "Canon",
        "model"        : "Canon EOS 5D Mark IV",
    },
    "extension"      : "jpg",
    "filename"       : "photo-1586348943529-beaae6c28db9",
    "height"         : 6272,
    "id"             : "lsoogGC_5dg",
    "liked_by_user"  : False,
    "likes"          : int,
    "location"       : {
        "city"    : "Beaver Dam",
        "country" : "United States",
        "name"    : "Beaver Dam, WI 53916, USA",
        "position": {
            "latitude" : 43.457769,
            "longitude": -88.837329,
        },
    },
    "promoted_at"    : "2020-04-08T15:12:03Z",
    "sponsorship"    : None,
    "tags"           : list,
    "updated_at"     : str,
    "user"           : {
        "accepted_tos"      : True,
        "bio"               : str,
        "first_name"        : "Dave",
        "id"                : "uMJXuywXLiU",
        "instagram_username": "just_midwest_rock",
        "last_name"         : "Hoefler",
        "location"          : None,
        "name"              : "Dave Hoefler",
        "portfolio_url"     : None,
        "total_collections" : int,
        "total_likes"       : int,
        "total_photos"      : int,
        "twitter_username"  : None,
        "updated_at"        : str,
        "username"          : "davehoefler",
    },
    "views"          : int,
    "width"          : 4480,
},

{
    "#url"     : "https://unsplash.com/@davehoefler",
    "#category": ("", "unsplash", "user"),
    "#class"   : unsplash.UnsplashUserExtractor,
    "#pattern" : r"https://images\.unsplash\.com/(photo-\d+-\w+|reserve/[^/?#]+)\?ixid=\w+&ixlib=rb-4\.0\.3$",
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://unsplash.com/@davehoefler/likes",
    "#category": ("", "unsplash", "favorite"),
    "#class"   : unsplash.UnsplashFavoriteExtractor,
    "#pattern" : r"https://images\.unsplash\.com/(photo-\d+-\w+|reserve/[^/?#]+)\?ixid=\w+&ixlib=rb-4\.0\.3$",
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://unsplash.com/collections/3178572/winter",
    "#category": ("", "unsplash", "collection"),
    "#class"   : unsplash.UnsplashCollectionExtractor,
    "#pattern" : r"https://images\.unsplash\.com/(photo-\d+-\w+|reserve/[^/?#]+)\?ixid=\w+&ixlib=rb-4\.0\.3$",
    "#range"   : "1-30",
    "#count"   : 30,

    "collection_id"   : "3178572",
    "collection_title": "winter",
},

{
    "#url"     : "https://unsplash.com/collections/3178572/",
    "#category": ("", "unsplash", "collection"),
    "#class"   : unsplash.UnsplashCollectionExtractor,
},

{
    "#url"     : "https://unsplash.com/collections/_8qJQ2bCMWE/2021.05",
    "#category": ("", "unsplash", "collection"),
    "#class"   : unsplash.UnsplashCollectionExtractor,
},

{
    "#url"     : "https://unsplash.com/s/photos/hair-style",
    "#category": ("", "unsplash", "search"),
    "#class"   : unsplash.UnsplashSearchExtractor,
    "#pattern" : r"https://(images|plus)\.unsplash\.com/((flagged/|premium_)?photo-\d+-\w+|reserve/[^/?#]+)\?ixid=\w+&ixlib=rb-4\.0\.3$",
    "#range"   : "1-30",
    "#count"   : 30,
},

)
