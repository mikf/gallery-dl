# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import everia


__tests__ = (
{
    "#url"  : "https://everia.club/2024/09/23/mikacho-조미카-joapictures-someday/",
    "#class": everia.EveriaPostExtractor,
    "#count": 32,

    "title"        : "Mikacho 조미카, JOApictures ‘Someday’",
    "post_category": "Korea",
    "tags"         : ["[JOApictures]", "Mikacho 조미카"]
},

{
    "#url"    : "https://everia.club/tag/miku-tanaka-%e7%94%b0%e4%b8%ad%e7%be%8e%e4%b9%85/",
    "#class"  : everia.EveriaTagExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#count"  : "> 50",
},

{
    "#url"    : "https://everia.club/category/japan/",
    "#class"  : everia.EveriaCategoryExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://everia.club/2023/10/05/",
    "#class"  : everia.EveriaDateExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#count"  : 34,
},

{
    "#url"    : "https://everia.club/?s=saika",
    "#class"  : everia.EveriaSearchExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#range"  : "1-15",
    "#count"  : 15,
},

)
