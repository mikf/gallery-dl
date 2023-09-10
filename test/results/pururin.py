# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pururin


__tests__ = (
{
    "#url"     : "https://pururin.to/gallery/38661/iowant-2",
    "#category": ("", "pururin", "gallery"),
    "#class"   : pururin.PururinGalleryExtractor,
    "#pattern" : r"https://i\.pururin\.to/38661/\d+\.jpg",

    "title"     : r"re:I ?owant 2!!",
    "title_en"  : r"re:I ?owant 2!!",
    "title_ja"  : "",
    "gallery_id": 38661,
    "count"     : 19,
    "artist"    : ["Shoda Norihiro"],
    "group"     : ["Obsidian Order"],
    "parody"    : ["Kantai Collection"],
    "characters": [
        "Iowa",
        "Teitoku",
    ],
    "tags"      : list,
    "type"      : "Doujinshi",
    "collection": ["I owant you!"],
    "convention": ["C92"],
    "rating"    : float,
    "uploader"  : "demo",
    "scanlator" : [
        "mrwayne",
        "The Lost Light",
    ],
    "lang"      : "en",
    "language"  : "English",
},

{
    "#url"     : "https://pururin.to/gallery/7661/unisis-team-vanilla",
    "#category": ("", "pururin", "gallery"),
    "#class"   : pururin.PururinGalleryExtractor,
    "#count"   : 17,
},

{
    "#url"     : "https://pururin.io/gallery/38661/iowant-2",
    "#category": ("", "pururin", "gallery"),
    "#class"   : pururin.PururinGalleryExtractor,
},

)
