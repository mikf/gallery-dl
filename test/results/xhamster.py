# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xhamster


__tests__ = (
{
    "#url"     : "https://xhamster.com/photos/gallery/take-me-to-the-carwash-at-digitaldesire-15860946",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
    "#pattern" : r"https://ic-ph-\w+\.xhcdn\.com/a/\w+/webp/000/\d+/\d+/\d+_1000\.jpg$",
    "#count"   : 19,

    "comments": int,
    "count"   : int,
    "favorite": bool,
    "id"      : int,
    "num"     : int,
    "height"  : int,
    "width"   : int,
    "imageURL": str,
    "pageURL" : str,
    "thumbURL": str,
    "gallery" : {
        "date"       : "dt:2022-02-02 06:30:09",
        "description": "Alina Henessy loves to wash her car, and we love seeing every inch of her gorgeous body. More at DigitalDesire.com",
        "dislikes"   : int,
        "id"         : 15860946,
        "likes"      : int,
        "tags"       : [
            "Babe",
            "Public Nudity",
            "Take",
            "Taking",
            "Masturbation",
            "Take Me",
        ],
        "thumbnail"  : str,
        "title"      : "Take me to the carwash at DigitalDesire",
        "views"      : range(100000, 200000),

    },
    "user"    : {
        "id"         : 4741860,
        "name"       : "DaringSex",
        "retired"    : False,
        "subscribers": range(25000, 50000),
        "url"        : "https://xhamster.com/users/daringsex",
        "verified"   : False,
    },
},

{
    "#url"     : "https://jp.xhamster2.com/photos/gallery/take-me-to-the-carwash-at-digitaldesire-15860946",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
    "#pattern" : r"https://ic-ph-\w+\.xhcdn\.com/a/\w+/webp/000/\d+/\d+/\d+_1000\.jpg$",
    "#count"   : 19,
},

{
    "#url"     : "https://xhamster.com/photos/gallery/make-the-world-better-11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
},

{
    "#url"     : "https://xhamster.com/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
},

{
    "#url"     : "https://xhamster.one/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
},

{
    "#url"     : "https://xhamster.desi/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
},

{
    "#url"     : "https://xhamster2.com/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
},

{
    "#url"     : "https://en.xhamster.com/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
},

{
    "#url"     : "https://xhamster.porncache.net/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
},

{
    "#url"     : "https://xhamster.com/users/daringsex/photos",
    "#category": ("", "xhamster", "user"),
    "#class"   : xhamster.XhamsterUserExtractor,
    "#pattern" : xhamster.XhamsterGalleryExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://xhamster.com/users/nickname68",
    "#category": ("", "xhamster", "user"),
    "#class"   : xhamster.XhamsterUserExtractor,
},

)
