# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hdoujin


__tests__ = (
{
    "#url"     : "https://hdoujin.org/g/119874/bd0a5217dfc6",
    "#class"   : hdoujin.HdoujinGalleryExtractor,
},

{
    "#url"     : "https://hdoujin.net/g/119874/bd0a5217dfc6",
    "#class"   : hdoujin.HdoujinGalleryExtractor,
},

{
    "#url"     : "https://hdoujin.org/browse?s=beach",
    "#class"   : hdoujin.HdoujinSearchExtractor,
},

{
    "#url"     : "https://hdoujin.org/tag/female:maid",
    "#class"   : hdoujin.HdoujinSearchExtractor,
    "#pattern" : hdoujin.HdoujinGalleryExtractor.pattern,
    "#range"   : "1-80",
    "#count"   : 80,
},

{
    "#url"     : "https://hdoujin.org/favorites",
    "#class"   : hdoujin.HdoujinFavoriteExtractor,
    "#auth"    : True,
},

)
