# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import flickr
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.flickr.com/photos/departingyyz/16089302239",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
    "#options" : {
        "contexts": True,
        "exif": True,
        "profile": True,
    },
    "#results"     : "https://live.staticflickr.com/7463/16089302239_de18cd8017_b_d.jpg",
    "#pattern"     : flickr.FlickrImageExtractor.pattern,
    "#sha1_content": [
        "3133006c6d657fe54cf7d4c46b82abbcb0efaf9f",
        "0821a28ee46386e85b02b67cf2720063440a228c",
    ],

    "camera"     : "Sony ILCE-7",
    "comments"   : int,
    "description": str,
    "exif"       : list,
    "extension"  : "jpg",
    "filename"   : "16089302239_de18cd8017_b_d",
    "id"         : 16089302239,
    "height"     : 683,
    "label"      : "Large",
    "license"    : "0",
    "license_name": "All Rights Reserved",
    "media"      : "photo",
    "pool"       : list,
    "set"        : list,
    "safety_level": "0",
    "tags"       : list,
    "url"        : str,
    "views"      : int,
    "width"      : 1024,

    "user": {
        "description": str,
        "has_adfree": 0,
        "has_free_educational_resources": 0,
        "has_free_standard_shipping": 0,
        "has_stats": 0,
        "iconfarm": 8,
        "iconserver": "7265",
        "id": "59437997@N05",
        "ispro": 0,
        "location": "Canada",
        "mobileurl": "https://www.flickr.com/photos/departingyyz/",
        "nsid": "59437997@N05",
        "path_alias": "departingyyz",
        "photosurl": "https://www.flickr.com/photos/departingyyz/",
        "profileurl": "https://www.flickr.com/people/departingyyz/",
        "realname": "Joshua Paul Shefman",
        "username": "departing(YYZ)",
        "photos": {
            "count": int,
            "firstdate": "1297577284",
            "firstdatetaken": "2008-07-07 18:31:47",
        },
        "timezone": {
            "label": "Eastern Time (US & Canada)",
            "offset": "-05:00",
            "timezone": 14,
            "timezone_id": "EST5EDT",
        },
    },
},

{
    "#url"     : "https://secure.flickr.com/photos/departingyyz/16089302239",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
},

{
    "#url"     : "https://m.flickr.com/photos/departingyyz/16089302239",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
},

{
    "#url"     : "https://flickr.com/photos/departingyyz/16089302239",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
},

{
    "#url"     : "https://www.flickr.com/photos/eliasroviello/52713899383/",
    "#comment" : "video",
    "#class"   : flickr.FlickrImageExtractor,
    "#pattern" : r"https://live.staticflickr\.com/video/52713899383/51dfffef79/1080p\.mp4\?s=ey.+",

    "media": "video",
},

{
    "#url"     : "http://c2.staticflickr.com/2/1475/24531000464_9a7503ae68_b.jpg",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
    "#pattern" : flickr.FlickrImageExtractor.pattern,
},

{
    "#url"     : "https://farm2.static.flickr.com/1035/1188352415_cb139831d0.jpg",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
    "#pattern" : flickr.FlickrImageExtractor.pattern,
},

{
    "#url"     : "https://flic.kr/p/FPVo9U",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
    "#pattern" : flickr.FlickrImageExtractor.pattern,

    "id"  : 26140204724,
    "date": "dt:2016-05-01 10:03:33",
    "user": {
        "location": "diebolsheim, france",
        "nsid": "23965455@N05",
        "path_alias": "sgu_",
        "realname": "philippe baumgart",
        "username": "philippe baumgart",
    },
},

{
    "#url"     : "https://www.flickr.com/photos/zzz/16089302238",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.flickr.com/photos/shona_s/albums/72157633471741607",
    "#category": ("", "flickr", "album"),
    "#class"   : flickr.FlickrAlbumExtractor,
    "#pattern" : flickr.FlickrImageExtractor.pattern,
    "#count"   : 6,
},

{
    "#url"     : "https://www.flickr.com/photos/shona_s/albums",
    "#category": ("", "flickr", "album"),
    "#class"   : flickr.FlickrAlbumExtractor,
    "#pattern" : flickr.FlickrAlbumExtractor.pattern,
    "#count"   : 2,
},

{
    "#url"     : "https://secure.flickr.com/photos/shona_s/albums",
    "#category": ("", "flickr", "album"),
    "#class"   : flickr.FlickrAlbumExtractor,
},

{
    "#url"     : "https://m.flickr.com/photos/shona_s/albums",
    "#category": ("", "flickr", "album"),
    "#class"   : flickr.FlickrAlbumExtractor,
},

{
    "#url"     : "https://www.flickr.com/photos/flickr/galleries/72157681572514792/",
    "#category": ("", "flickr", "gallery"),
    "#class"   : flickr.FlickrGalleryExtractor,
    "#pattern" : flickr.FlickrImageExtractor.pattern,
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.flickr.com/groups/bird_headshots/",
    "#category": ("", "flickr", "group"),
    "#class"   : flickr.FlickrGroupExtractor,
    "#pattern" : flickr.FlickrImageExtractor.pattern,
    "#count"   : "> 150",
},

{
    "#url"     : "https://www.flickr.com/photos/shona_s/",
    "#category": ("", "flickr", "user"),
    "#class"   : flickr.FlickrUserExtractor,
    "#pattern" : flickr.FlickrImageExtractor.pattern,
    "#count"   : 28,
},

{
    "#url"     : "https://www.flickr.com/photos/shona_s/favorites",
    "#category": ("", "flickr", "favorite"),
    "#class"   : flickr.FlickrFavoriteExtractor,
    "#options" : {
        "info": True,
        "profile": True,
    },
    "#results" : (
        "https://live.staticflickr.com/7322/8719105033_4a21140220_o_d.jpg",
        "https://live.staticflickr.com/7376/8720226282_eae0faefd1_o_d.jpg",
        "https://live.staticflickr.com/7460/8720245516_ab06f80353_o_d.jpg",
        "https://live.staticflickr.com/8268/8705102120_64349ebac2_o_d.jpg",
    ),

    "dates"       : dict,
    "license"     : "0",
    "license_name": "All Rights Reserved",
    "notes"       : dict,
    "safety_level": "0",
    "owner": {
        "iconfarm"  : int,
        "iconserver": str,
        "location"  : None,
        "nsid"      : str,
        "path_alias": None,
        "realname"  : str,
        "username"  : str,
    },
    "user": {
        "nsid": "95410434@N08",
        "path_alias": "shona_s",
        "username": "Shona_S",

        "description": "",
        "has_adfree": 0,
        "has_free_educational_resources": 0,
        "has_free_standard_shipping": 0,
        "has_stats": 0,
        "iconfarm": 0,
        "iconserver": "0",
        "id": "95410434@N08",
        "ispro": 0,
        "mobileurl": "https://www.flickr.com/photos/shona_s/",
        "photosurl": "https://www.flickr.com/photos/shona_s/",
        "profileurl": "https://www.flickr.com/people/shona_s/",
        "photos": {
            "count": 28,
            "firstdate": "1367947187",
            "firstdatetaken": "2012-09-21 19:35:39",
        },
    },
},

{
    "#url"     : "https://flickr.com/search/?text=mountain",
    "#category": ("", "flickr", "search"),
    "#class"   : flickr.FlickrSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
    "#pattern" : r"https://live\.staticflickr\.com/\d+/.+",

    "search": {
        "text": "mountain",
    },
},

{
    "#url"     : "https://flickr.com/search/?text=tree%20cloud%20house&color_codes=4&styles=minimalism",
    "#category": ("", "flickr", "search"),
    "#class"   : flickr.FlickrSearchExtractor,
},

)
