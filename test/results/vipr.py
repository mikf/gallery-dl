# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://vipr.im/kcd5jcuhgs3v.html",
    "#category": ("imagehost", "vipr", "image"),
    "#class"   : imagehosts.ViprImageExtractor,
    "#results" : "https://i7.vipr.im/i/00021/kcd5jcuhgs3v.jpg/sommer01035.jpg",

    "extension": "jpg",
    "filename" : "sommer01035",
    "post_url" : "https://vipr.im/kcd5jcuhgs3v",
    "token"    : "kcd5jcuhgs3v",
},

{
    "#url"     : "https://vipr.im/yyqomiutt768",
    "#category": ("imagehost", "vipr", "image"),
    "#class"   : imagehosts.ViprImageExtractor,
    "#exception": "NotFoundError",
},

)
