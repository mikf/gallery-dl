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
    "#pattern"     : flickr.FlickrImageExtractor.pattern,
    "#sha1_content": [
        "3133006c6d657fe54cf7d4c46b82abbcb0efaf9f",
        "0821a28ee46386e85b02b67cf2720063440a228c",
    ],

    "comments"   : int,
    "description": str,
    "extension"  : "jpg",
    "filename"   : "16089302239_de18cd8017_b",
    "id"         : 16089302239,
    "height"     : 683,
    "label"      : "Large",
    "media"      : "photo",
    "url"        : str,
    "views"      : int,
    "width"      : 1024,
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
    "#url"     : "https://www.flickr.com/photos/145617051@N08/46733161535",
    "#category": ("", "flickr", "image"),
    "#class"   : flickr.FlickrImageExtractor,
    "#count"   : 1,

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
    "#pattern" : flickr.FlickrImageExtractor.pattern,
    "#count"   : 4,
},

{
    "#url"     : "https://flickr.com/search/?text=mountain",
    "#category": ("", "flickr", "search"),
    "#class"   : flickr.FlickrSearchExtractor,
},

{
    "#url"     : "https://flickr.com/search/?text=tree%20cloud%20house&color_codes=4&styles=minimalism",
    "#category": ("", "flickr", "search"),
    "#class"   : flickr.FlickrSearchExtractor,
},

)
