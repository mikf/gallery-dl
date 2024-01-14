# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import kemonoparty


__tests__ = (
{
    "#url"     : "https://coomer.su/onlyfans/user/alinity/post/125962203",
    "#comment" : "coomer (#2100)",
    "#category": ("", "coomerparty", "onlyfans"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#urls"    : "https://coomer.su/data/7d/3f/7d3fd9804583dc224968c0591163ec91794552b04f00a6c2f42a15b68231d5a8.jpg",
},

{
    "#url"     : "https://coomer.party/onlyfans/user/alinity/post/125962203",
    "#category": ("", "coomerparty", "onlyfans"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#urls"    : "https://coomer.party/data/7d/3f/7d3fd9804583dc224968c0591163ec91794552b04f00a6c2f42a15b68231d5a8.jpg",
},

)
