# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://commons.wikimedia.org/wiki/File:Starr-050516-1367-Pimenta_dioica-flowers-Maunaloa-Molokai_(24762757525).jpg",
    "#category": ("wikimedia", "wikimediacommons", "file"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#results" : "https://upload.wikimedia.org/wikipedia/commons/f/fa/Starr-050516-1367-Pimenta_dioica-flowers-Maunaloa-Molokai_%2824762757525%29.jpg?format=original",
},

{
    "#url"     : "https://commons.wikimedia.org/wiki/Category:Network_maps_of_the_Paris_Metro",
    "#category": ("wikimedia", "wikimediacommons", "category"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://commons.wikimedia.org/wiki/Category:Ivan_Shishkin",
    "#comment" : "subcategories",
    "#category": ("wikimedia", "wikimediacommons", "category"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#options" : {"image-filter": "False"},

    "#results": (
        "https://commons.wikimedia.org/wiki/Category:3558_Shishkin",
        "https://commons.wikimedia.org/wiki/Category:Drawings_by_Ivan_Shishkin",
        "https://commons.wikimedia.org/wiki/Category:Ivan_Shishkin_grave",
        "https://commons.wikimedia.org/wiki/Category:Ivan_Shishkin_in_art",
        "https://commons.wikimedia.org/wiki/Category:Ivan_Shishkin._To_the_190th_anniversary_of_the_birth",
        "https://commons.wikimedia.org/wiki/Category:Paintings_by_Ivan_Shishkin",
        "https://commons.wikimedia.org/wiki/Category:Shishkin_Street_(Martyshkino)",
        "https://commons.wikimedia.org/wiki/Category:Shishkin_street,_Moscow",
        "https://commons.wikimedia.org/wiki/Category:Shishkin's_Pine",
    ),
},

)
