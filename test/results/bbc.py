# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bbc


__tests__ = (
{
    "#url"     : "https://www.bbc.co.uk/programmes/p084qtzs/p085g9kg",
    "#category": ("", "bbc", "gallery"),
    "#class"   : bbc.BbcGalleryExtractor,
    "#pattern" : r"https://ichef\.bbci\.co\.uk/images/ic/1920xn/\w+\.jpg",
    "#count"   : 37,

    "programme": "p084qtzs",
    "path"     : [
        "BBC One",
        "Doctor Who",
        "The Timeless Children",
    ],
},

{
    "#url"     : "https://www.bbc.co.uk/programmes/p084qtzs",
    "#category": ("", "bbc", "gallery"),
    "#class"   : bbc.BbcGalleryExtractor,
},

{
    "#url"     : "https://www.bbc.co.uk/programmes/b006q2x0/galleries",
    "#category": ("", "bbc", "programme"),
    "#class"   : bbc.BbcProgrammeExtractor,
    "#pattern" : bbc.BbcGalleryExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : ">= 50",
},

{
    "#url"     : "https://www.bbc.co.uk/programmes/b006q2x0/galleries?page=25",
    "#category": ("", "bbc", "programme"),
    "#class"   : bbc.BbcProgrammeExtractor,
    "#pattern" : bbc.BbcGalleryExtractor.pattern,
    "#count"   : ">= 100",
},

)
