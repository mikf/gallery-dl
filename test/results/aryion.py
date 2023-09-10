# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import aryion


__tests__ = (
{
    "#url"     : "https://aryion.com/g4/gallery/jameshoward",
    "#category": ("", "aryion", "gallery"),
    "#class"   : aryion.AryionGalleryExtractor,
    "#options" : {"recursive": False},
    "#pattern" : r"https://aryion\.com/g4/data\.php\?id=\d+$",
    "#range"   : "48-52",
    "#count"   : 5,
},

{
    "#url"     : "https://aryion.com/g4/user/jameshoward",
    "#category": ("", "aryion", "gallery"),
    "#class"   : aryion.AryionGalleryExtractor,
},

{
    "#url"     : "https://aryion.com/g4/latest.php?name=jameshoward",
    "#category": ("", "aryion", "gallery"),
    "#class"   : aryion.AryionGalleryExtractor,
},

{
    "#url"     : "https://aryion.com/g4/tags.php?tag=star+wars&p=19",
    "#category": ("", "aryion", "tag"),
    "#class"   : aryion.AryionTagExtractor,
    "#count"   : ">= 5",
},

{
    "#url"     : "https://aryion.com/g4/view/510079",
    "#category": ("", "aryion", "post"),
    "#class"   : aryion.AryionPostExtractor,
    "#sha1_url": "f233286fa5558c07ae500f7f2d5cb0799881450e",

    "artist"     : "jameshoward",
    "user"       : "jameshoward",
    "filename"   : "jameshoward-510079-subscribestar_150",
    "extension"  : "jpg",
    "id"         : 510079,
    "width"      : 1665,
    "height"     : 1619,
    "size"       : 784239,
    "title"      : "I'm on subscribestar now too!",
    "description": r"re:Doesn't hurt to have a backup, right\?",
    "tags"       : [
        "Non-Vore",
        "subscribestar",
    ],
    "date"       : "dt:2019-02-16 19:30:34",
    "path"       : [],
    "views"      : int,
    "favorites"  : int,
    "comments"   : int,
    "_mtime"     : "Sat, 16 Feb 2019 19:30:34 GMT",
},

{
    "#url"     : "https://aryion.com/g4/view/588928",
    "#comment" : "x-folder (#694)",
    "#category": ("", "aryion", "post"),
    "#class"   : aryion.AryionPostExtractor,
    "#pattern" : aryion.AryionPostExtractor.pattern,
    "#count"   : ">= 8",
},

{
    "#url"     : "https://aryion.com/g4/view/537379",
    "#comment" : "x-comic-folder (#945)",
    "#category": ("", "aryion", "post"),
    "#class"   : aryion.AryionPostExtractor,
    "#pattern" : aryion.AryionPostExtractor.pattern,
    "#count"   : 2,
},

)
