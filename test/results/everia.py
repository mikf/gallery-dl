# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import everia


__tests__ = (
{
    "#url"      : "https://everia.club/2024/09/23/mikacho-조미카-joapictures-someday/",
    "#category" : ("", "everia", "post"),
    "#class"    : everia.EveriaPostExtractor,
    "#archive"  : False,
    "#count"    : 32,

    "title"     : "Mikacho 조미카, JOApictures ‘Someday’",
    "post_category": "Korea",
    "tags"      : ["[JOApictures]", "Mikacho 조미카"]
},
{
    "#url"      : "https://everia.club/tag/yeon-woo-연우/",
    "#category" : ("", "everia", "tag"),
    "#class"    : everia.EveriaTagExtractor,
},
{
    "#url"      : "https://everia.club/category/japan/",
    "#category" : ("", "everia", "category"),
    "#class"    : everia.EveriaCategoryExtractor,
},
{
    "#url"      : "https://everia.club/?s=saika",
    "#category" : ("", "everia", "search"),
    "#class"    : everia.EveriaSearchExtractor,
}
)
