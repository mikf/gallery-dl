# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://imx.to/i/1qdeva",
    "#comment" : "new-style URL",
    "#category": ("imagehost", "imxto", "image"),
    "#class"   : imagehosts.ImxtoImageExtractor,
    "#results"     : "https://image.imx.to/u/i/2018/04/09/1qdeva.png",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "filename" : "test-ãƒ†ã‚¹ãƒˆ",
    "extension": "png",
    "post_url" : "https://imx.to/i/1qdeva",
    "size"  : 18,
    "width" : 64,
    "height": 32,
    "token" : "1qdeva",
    "hash"  : "94d56c599223c59f3feb71ea603484d1",
},

{
    "#url"     : "https://imx.to/img-57a2050547b97.html",
    "#comment" : "old-style URL",
    "#category": ("imagehost", "imxto", "image"),
    "#class"   : imagehosts.ImxtoImageExtractor,
    "#results"     : "https://image.imx.to/u/i/2016/08/03/57a2050547b60.jpg",
    "#sha1_content": "54592f2635674c25677c6872db3709d343cdf92f",

    "filename" : "test",
    "extension": "jpg",
    "post_url" : "https://imx.to/img-57a2050547b97.html",
    "size"  : 5284,
    "width" : 320,
    "height": 160,
    "token" : "57a2050547b97",
    "hash"  : "40da6aaa7b8c42b18ef74309bbc713fc",
},

{
    "#url"     : "https://img.yt/img-57a2050547b97.html",
    "#comment" : "img.yt domain",
    "#category": ("imagehost", "imxto", "image"),
    "#class"   : imagehosts.ImxtoImageExtractor,
    "#results" : "https://image.imx.to/u/i/2016/08/03/57a2050547b60.jpg",

    "filename" : "test",
    "extension": "jpg",
    "post_url" : "https://imx.to/img-57a2050547b97.html",
    "size"  : 5284,
    "width" : 320,
    "height": 160,
    "token" : "57a2050547b97",
    "hash"  : "40da6aaa7b8c42b18ef74309bbc713fc",
},

{
    "#url"     : "https://imx.to/img-57a2050547b98.html",
    "#category": ("imagehost", "imxto", "image"),
    "#class"   : imagehosts.ImxtoImageExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://imx.to/g/ozdy",
    "#category": ("imagehost", "imxto", "gallery"),
    "#class"   : imagehosts.ImxtoGalleryExtractor,
    "#pattern" : imagehosts.ImxtoImageExtractor.pattern,
    "#count"   : 40,

    "title": "untitled gallery",
},

{
    "#url"     : "https://imx.to/g/mgun",
    "#comment" : "multiple pages (#8282)",
    "#category": ("imagehost", "imxto", "gallery"),
    "#class"   : imagehosts.ImxtoGalleryExtractor,
    "#pattern" : imagehosts.ImxtoImageExtractor.pattern,
    "#count"   : 1037,

    "title": "freckledspirit",
},

)
