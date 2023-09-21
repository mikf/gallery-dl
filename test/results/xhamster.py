# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xhamster


__tests__ = (
{
    "#url"     : "https://xhamster.com/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
    "#pattern" : r"https://thumb-p\d+.xhcdn.com/./[\w/-]+_1000.jpg$",
    "#count"   : ">= 144",

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
        "date"       : "dt:2019-04-16 00:07:31",
        "description": "",
        "dislikes"   : int,
        "id"         : 11748968,
        "likes"      : int,
        "tags"       : ["NON-Porn"],
        "thumbnail"  : str,
        "title"      : "Make the world better.",
        "views"      : int,
    },
    "user"    : {
        "id"         : 16874672,
        "name"       : "Anonymousrants",
        "retired"    : bool,
        "subscribers": int,
        "url"        : "https://xhamster.com/users/anonymousrants",
        "verified"   : bool,
    },
},

{
    "#url"     : "https://jp.xhamster2.com/photos/gallery/11748968",
    "#category": ("", "xhamster", "gallery"),
    "#class"   : xhamster.XhamsterGalleryExtractor,
    "#pattern" : r"https://thumb-p\d+.xhcdn.com/./[\w/-]+_1000.jpg$",
    "#count"   : ">= 144",
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
    "#url"     : "https://xhamster.com/users/goldenpalomino/photos",
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
