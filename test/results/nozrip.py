# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://noz.rip/booru/post/view/29",
    "#category": ("shimmie2", "nozrip", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#results" : "https://noz.rip/booru/_images/f33d9e0da3ba476f67ef18911e05876b/29%20-%20inkling%20series%3Asplatoon%20unknown_artist%20wat.png",

    "id"       : 29,
    "filename" : "29 - inkling series:splatoon unknown_artist wat",
    "extension": "png",
    "file_url" : "https://noz.rip/booru/_images/f33d9e0da3ba476f67ef18911e05876b/29%20-%20inkling%20series%3Asplatoon%20unknown_artist%20wat.png",
    "width"    : 798,
    "height"   : 598,
    "md5"      : "f33d9e0da3ba476f67ef18911e05876b",
    "size"     : 0,
    "tags"     : "inkling series:splatoon unknown_artist wat",
},

{
    "#url"     : "https://noz.rip/booru/post/list/inkling/1",
    "#category": ("shimmie2", "nozrip", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://noz\.rip/booru/_images/[0-9a-f]{32}/\d+.+\.\w+",
    "#count"   : range(130, 150),

    "id"         : int,
    "filename"   : str,
    "extension"  : {"jpeg", "jpg", "png"},
    "file_url"   : str,
    "width"      : int,
    "height"     : int,
    "size"       : int,
    "md5"        : "len:str:32",
    "search_tags": "inkling",
    "tags"       : str,
},

)
