# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import chevereto


__tests__ = (
{
    "#url"     : "https://img.kiwi/image/79de2c41-70f9-4a87-bd6d-00fe9997c0c4.JR2wZz",
    "#category": ("chevereto", "imgkiwi", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#urls"        : "https://img.kiwi/images/2023/02/28/11ac1ebf28a2eae8265026b28e9c4413.jpg",
    "#sha1_content": "9ea704a77e2038b9008350682cfad53a614a60bd",

    "album"    : "Kins3y Wolansk1",
    "extension": "jpg",
    "filename" : "11ac1ebf28a2eae8265026b28e9c4413",
    "id"       : "JR2wZz",
    "url"      : "https://img.kiwi/images/2023/02/28/11ac1ebf28a2eae8265026b28e9c4413.jpg",
    "user"     : "johnirl",
},

{
    "#url"     : "https://img.kiwi/album/kins3y-wolansk1.8Jxc",
    "#category": ("chevereto", "imgkiwi", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#pattern" : chevereto.CheveretoImageExtractor.pattern,
    "#count"   : 19,
},

{
    "#url"     : "https://img.kiwi/johnirl",
    "#category": ("chevereto", "imgkiwi", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#pattern" : chevereto.CheveretoImageExtractor.pattern,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://img.kiwi/johnirl/albums",
    "#category": ("chevereto", "imgkiwi", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#pattern" : chevereto.CheveretoAlbumExtractor.pattern,
    "#count"   : range(155, 175),
},

)
