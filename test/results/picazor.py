# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import picazor


__tests__ = (
{
    "#url"     : "https://picazor.com/en/kailey-mae",
    "#class"   : picazor.PicazorUserExtractor,
    "#range"   : "1-50",
    "#pattern" : r"https://picazor\.com/uploads/.+\.jpg",
    "#count"   : 50,

    "count"    : 278,
    "num"      : range(200, 278),
    "extension": "jpg",
    "filename" : str,
    "id"       : "re:[0-9a-f]+",
    "mime"     : "photo",
    "path"     : str,
    "user"     : "kailey-mae",
    "visible"  : True,
    "subject"  : {
        "id" : "66077ba2b64e3f3d178f39ac",
        "uri": "kailey-mae",
    },
},

{
    "#url"     : "https://picazor.com/vi/badassnugget",
    "#comment" : "non-'en' language code",
    "#class"   : picazor.PicazorUserExtractor,
},

)
