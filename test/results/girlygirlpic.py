# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import girlygirlpic
import datetime


__tests__ = (
{
    "#url"     : "https://en.girlygirlpic.com/a/3np2t1zt2v",
    "#category": ("", "girlygirlpic", "album"),
    "#class"   : girlygirlpic.GirlygirlpicAlbumExtractor,
    "#archive" : False,
    "#count"   : 75,

    "title"    : "[Showman XiuRen] No.4480 Yang Chenchen",
    "model"    : "Yang Chenchen",
    "date"     : datetime.datetime,
    "tags"     : ["Alice T", "Leggings"]
},
{
    "#url"     : "https://en.girlygirlpic.com/m/7cywcgv",
    "#category": ("", "girlygirlpic", "model"),
    "#class"   : girlygirlpic.GirlygirlpicModelExtractor,
},
{
    "#url"     : "https://en.girlygirlpic.com/c/2cef8ad",
    "#category": ("", "girlygirlpic", "studio"),
    "#class"   : girlygirlpic.GirlygirlpicStudioExtractor,
},
{
    "#url"     : "https://en.girlygirlpic.com/t/73se3i3",
    "#category": ("", "girlygirlpic", "tag"),
    "#class"   : girlygirlpic.GirlygirlpicTagExtractor,
},
{
    "#url"     : "https://en.girlygirlpic.com/l/4jwcwsp",
    "#category": ("", "girlygirlpic", "region"),
    "#class"   : girlygirlpic.GirlygirlpicRegionExtractor,
},
{
    "#url"     : "https://en.girlygirlpic.com/s/graphis",
    "#category": ("", "girlygirlpic", "search"),
    "#class"   : girlygirlpic.GirlygirlpicSearchExtractor,
},
)
