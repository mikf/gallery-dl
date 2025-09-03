# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://co.llection.pics/post/view/23",
    "#category": ("shimmie2", "thecollectionS", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#results" : "https://co.llection.pics/_images/0f431221d96251e6db62cb2c57f5b29f/23%20-%20crossovers%20dc%20goku%20kal-el%20superman.jpg",

    "extension": "jpg",
    "file_url" : "https://co.llection.pics/_images/0f431221d96251e6db62cb2c57f5b29f/23%20-%20crossovers%20dc%20goku%20kal-el%20superman.jpg",
    "filename" : "23 - crossovers dc goku kal-el superman",
    "height"   : 628,
    "id"       : 23,
    "md5"      : "0f431221d96251e6db62cb2c57f5b29f",
    "size"     : 0,
    "tags"     : "crossovers dc goku kal-el superman",
    "width"    : 1124,
},

{
    "#url"     : "https://co.llection.pics/post/list/crossovers/1",
    "#category": ("shimmie2", "thecollectionS", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#range"   : "1-80",
    "#pattern" : r"https://co\.llection\.pics/_images/\w{32}/\d+.+\.(jpe?g|png|gif)",
    "#count"   : 80,

    "id"         : int,
    "filename"   : str,
    "extension"  : {"jpg", "jpeg", "png", "gif"},
    "file_url"   : r"re:https://co.llection.pics/_images/\w{32}/.+",
    "width"      : range(100, 8_000),
    "height"     : range(100, 8_000),
    "md5"        : r"re:\w{32}",
    "search_tags": "crossovers",
    "size"       : range(1_000, 8_000_000),
    "tags"       : str,
},

)
