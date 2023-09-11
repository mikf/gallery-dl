# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.35photo")
_35photo = getattr(gallery_dl.extractor, "35photo")


__tests__ = (
{
    "#url"     : "https://35photo.pro/liya",
    "#category": ("", "35photo", "user"),
    "#class"   : _35photo._35photoUserExtractor,
    "#pattern" : r"https://([a-z][0-9]\.)?35photo\.pro/photos_(main|series)/.*\.jpg",
    "#count"   : 9,
},

{
    "#url"     : "https://35photo.pro/suhoveev",
    "#comment" : "last photo ID (1267028) isn't given as 'photo-id=\"<id>\" - "
                 "there are only 23 photos without the last one",
    "#category": ("", "35photo", "user"),
    "#class"   : _35photo._35photoUserExtractor,
    "#count"   : ">= 33",
},

{
    "#url"     : "https://en.35photo.pro/liya",
    "#category": ("", "35photo", "user"),
    "#class"   : _35photo._35photoUserExtractor,
},

{
    "#url"     : "https://ru.35photo.pro/liya",
    "#category": ("", "35photo", "user"),
    "#class"   : _35photo._35photoUserExtractor,
},

{
    "#url"     : "https://35photo.pro/tags/landscape/",
    "#category": ("", "35photo", "tag"),
    "#class"   : _35photo._35photoTagExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
    "#archive" : False,
},

{
    "#url"     : "https://35photo.pro/genre_109/",
    "#category": ("", "35photo", "genre"),
    "#class"   : _35photo._35photoGenreExtractor,
},

{
    "#url"     : "https://35photo.pro/photo_753340/",
    "#category": ("", "35photo", "image"),
    "#class"   : _35photo._35photoImageExtractor,
    "#count"   : 1,

    "url"        : r"re:https://35photo\.pro/photos_main/.*\.jpg",
    "id"         : 753340,
    "title"      : "Winter walk",
    "description": str,
    "tags"       : list,
    "views"      : int,
    "favorites"  : int,
    "score"      : int,
    "type"       : 0,
    "date"       : "15 авг, 2014",
    "user"       : "liya",
    "user_id"    : 20415,
    "user_name"  : "Liya Mirzaeva",
},

)
