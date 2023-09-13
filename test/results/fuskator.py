# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fuskator


__tests__ = (
{
    "#url"     : "https://fuskator.com/thumbs/d0GnIzXrSKU/",
    "#category": ("", "fuskator", "gallery"),
    "#class"   : fuskator.FuskatorGalleryExtractor,
    "#pattern" : r"https://i\d+.fuskator.com/large/d0GnIzXrSKU/.+\.jpg",
    "#count"   : 22,

    "gallery_id"  : 473023,
    "gallery_hash": "d0GnIzXrSKU",
    "title"       : r"re:Shaved Brunette Babe Maria Ryabushkina with ",
    "views"       : int,
    "score"       : float,
    "count"       : 22,
    "tags"        : list,
},

{
    "#url"     : "https://fuskator.com/expanded/gXpKzjgIidA/index.html",
    "#category": ("", "fuskator", "gallery"),
    "#class"   : fuskator.FuskatorGalleryExtractor,
},

{
    "#url"     : "https://fuskator.com/search/red_swimsuit/",
    "#category": ("", "fuskator", "search"),
    "#class"   : fuskator.FuskatorSearchExtractor,
    "#pattern" : fuskator.FuskatorGalleryExtractor.pattern,
    "#count"   : ">= 40",
},

{
    "#url"     : "https://fuskator.com/page/3/swimsuit/quality/",
    "#category": ("", "fuskator", "search"),
    "#class"   : fuskator.FuskatorSearchExtractor,
},

)
