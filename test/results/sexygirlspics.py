# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import sexygirlspics


__tests__ = (
{
    "#url"     : "https://sexygirlspics.com/shaved/",
    "#category": ("", "sexygirlspics", "tag"),
    "#class"   : sexygirlspics.SexygirlspicsTagExtractor,
    "#pattern" : sexygirlspics.SexygirlspicsAlbumExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://sexygirlspics.com/pics/blonde-teen-ashlee-cox-has-a-threesome-with-a-couple-on-their-bed-98021229/",
    "#category": ("", "sexygirlspics", "gallery"),
    "#class"   : sexygirlspics.SexygirlspicsAlbumExtractor,
    "#pattern" : r"https://cdni\\.sexygirlspics\\.com/1280/.+\\.jpg",
    "#count"   : 16,
    "#results" : "https://cdni.sexygirlspics.com/1280/1/334/98021229/98021229_001_6851.jpg",

    "gallery_id": 98021229,
    "slug"      : "blonde-teen-ashlee-cox-has-a-threesome-with-a-couple-on-their-bed-98021229",
    "title"     : "Blonde teen Ashlee Cox has a threesome with a couple on their bed",
},
)
