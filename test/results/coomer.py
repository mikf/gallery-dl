# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import kemono


__tests__ = (
{
    "#url"     : "https://coomer.st/onlyfans/user/alinity/post/125962203",
    "#comment" : "coomer (#2100)",
    "#category": ("", "coomer", "onlyfans"),
    "#class"   : kemono.KemonoPostExtractor,
    "#results" : "https://coomer.st/data/7d/3f/7d3fd9804583dc224968c0591163ec91794552b04f00a6c2f42a15b68231d5a8.jpg",
},

{
    "#url"     : "https://coomer.su/onlyfans/user/alinity/post/125962203",
    "#comment" : "legacy TLD",
    "#category": ("", "coomer", "onlyfans"),
    "#class"   : kemono.KemonoPostExtractor,
},

{
    "#url"     : "https://coomer.party/onlyfans/user/alinity/post/125962203",
    "#comment" : "legacy TLD",
    "#category": ("", "coomer", "onlyfans"),
    "#class"   : kemono.KemonoPostExtractor,
},

{
    "#url"     : "https://coomer.party/onlyfans/user/alinity/post/125962203",
    "#category": ("", "coomer", "onlyfans"),
    "#class"   : kemono.KemonoPostExtractor,
    "#results" : "https://coomer.st/data/7d/3f/7d3fd9804583dc224968c0591163ec91794552b04f00a6c2f42a15b68231d5a8.jpg",
},

)
