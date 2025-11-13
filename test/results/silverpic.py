# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://www.silverpic.net/8k562jyix8xq/jxU_0001.JPG.html",
    "#category": ("imagehost", "silverpic", "image"),
    "#class"   : imagehosts.SilverpicImageExtractor,
    "#results" : "https://silverpic.net/img/z7esmp7eor37ssodt4ptpxbzoy/jxU_0001.JPG",

    "filename" : "jxU_0001",
    "extension": "jpg",
    "token"    : "8k562jyix8xq",
    "width"    : 3744,
    "height"   : 5616,
},

{
    "#url"     : "https://www.silverpic.com/8k562jyix8xq/jxU_0001.JPG.html",
    "#category": ("imagehost", "silverpic", "image"),
    "#class"   : imagehosts.SilverpicImageExtractor,
    "#results" : "https://silverpic.net/img/z7esmp7eor37ssodt4ptpxbzoy/jxU_0001.JPG",
},

)
