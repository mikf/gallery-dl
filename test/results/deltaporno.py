# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import chevereto


__tests__ = (
{
    "#url"     : "https://gallery.deltaporno.com/image/7af6c7e241c600cd83dffdb22d4a1bb83336ede3b04bf406b36abf7b6f7dc4d8.8Gchu",
    "#category": ("chevereto", "deltaporno", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#urls"        : "https://gallery.deltaporno.com/images/2023/02/16/7af6c7e241c600cd83dffdb22d4a1bb83336ede3b04bf406b36abf7b6f7dc4d82e43ec48389730d4.jpg",
    "#sha1_content": "f7e2a138b00c0742ccd77ab4031703bd8cc5b5a7",

    "album"    : "Urmumanddad321 nude",
    "extension": "jpg",
    "filename" : "7af6c7e241c600cd83dffdb22d4a1bb83336ede3b04bf406b36abf7b6f7dc4d82e43ec48389730d4",
    "id"       : "8Gchu",
    "url"      : "https://gallery.deltaporno.com/images/2023/02/16/7af6c7e241c600cd83dffdb22d4a1bb83336ede3b04bf406b36abf7b6f7dc4d82e43ec48389730d4.jpg",
    "user"     : "delta",
},

{
    "#url"     : "https://gallery.deltaporno.com/album/urmumanddad321-nude.RqCYu",
    "#category": ("chevereto", "deltaporno", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#pattern" : chevereto.CheveretoImageExtractor.pattern,
    "#count"   : 28,
    "#sha1_url": "fab8121bce72a9db2d1ed1e7520317a7a454d6c5",
},

{
    "#url"     : "https://gallery.deltaporno.com/delta",
    "#category": ("chevereto", "deltaporno", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
},

)
