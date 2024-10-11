# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import girlgirlgo
import datetime


__tests__ = (
{
    "#url"     : "https://en.girlgirlgo.org/a/3np2t1zt2v",
    "#category": ("", "girlgirlgo", "album"),
    "#class"   : girlgirlgo.GirlgirlgoAlbumExtractor,
    "#archive" : False,
    "#count"   : 75,
    
    "title"    : "[Showman XiuRen] No.4480 Yang Chenchen",
    "model"    : "Yang Chenchen",
    "date"     : datetime.datetime,
    "tags"     : ["Alice T", "Leggings"]
},
{
    "#url"     : "https://en.girlgirlgo.org/m/7cywcgv",
    "#category": ("", "girlgirlgo", "model"),
    "#class"   : girlgirlgo.GirlgirlgoModelExtractor,
},
{
    "#url"     : "https://en.girlgirlgo.org/c/2cef8ad",
    "#category": ("", "girlgirlgo", "studio"),
    "#class"   : girlgirlgo.GirlgirlgoStudioExtractor,
},
{
    "#url"     : "https://en.girlgirlgo.org/t/73se3i3",
    "#category": ("", "girlgirlgo", "tag"),
    "#class"   : girlgirlgo.GirlgirlgoTagExtractor,
},
{
    "#url"     : "https://en.girlgirlgo.org/l/4jwcwsp",
    "#category": ("", "girlgirlgo", "region"),
    "#class"   : girlgirlgo.GirlgirlgoRegionExtractor,
},
{
    "#url"     : "https://en.girlgirlgo.org/s/4ab1m8ccdu",
    "#category": ("", "girlgirlgo", "search"),
    "#class"   : girlgirlgo.GirlgirlgoSearchExtractor,
},
)
