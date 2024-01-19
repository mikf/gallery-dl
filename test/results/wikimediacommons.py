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
    "#urls"    : "https://upload.wikimedia.org/wikipedia/commons/f/fa/Starr-050516-1367-Pimenta_dioica-flowers-Maunaloa-Molokai_%2824762757525%29.jpg",
},

{
    "#url"     : "https://commons.wikimedia.org/wiki/Category:Network_maps_of_the_Paris_Metro",
    "#category": ("wikimedia", "wikimediacommons", "category"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
