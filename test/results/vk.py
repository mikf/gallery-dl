# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vk
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://vk.com/id398982326",
    "#category": ("", "vk", "photos"),
    "#class"   : vk.VkPhotosExtractor,
    "#pattern" : r"https://sun\d+-\d+\.userapi\.com/c\d+/v\d+/\w+/[\w-]+\.\w+",
    "#count"   : ">= 35",

    "id"  : r"re:\d+",
    "user": {
        "id"  : "398982326",
        "info": "Мы за Движуху! – m1ni SounD #4 [EROmusic]",
        "name": "",
        "nick": "Dobrov Kurva",
    },
},

{
    "#url"     : "https://vk.com/cosplayinrussia",
    "#category": ("", "vk", "photos"),
    "#class"   : vk.VkPhotosExtractor,
    "#range"   : "15-25",

    "id"  : r"re:\d+",
    "user": {
        "id"  : "-165740836",
        "info": str,
        "name": "cosplayinrussia",
        "nick": "Косплей | Cosplay 18+",
    },
},

{
    "#url"     : "https://vk.com/id76957806",
    "#comment" : "photos without width/height (#2535)",
    "#category": ("", "vk", "photos"),
    "#class"   : vk.VkPhotosExtractor,
    "#pattern" : r"https://sun\d+-\d+\.userapi\.com/",
    "#range"   : "1-9",
    "#count"   : 9,
},

{
    "#url"     : "https://m.vk.com/albums398982326",
    "#category": ("", "vk", "photos"),
    "#class"   : vk.VkPhotosExtractor,
},

{
    "#url"     : "https://www.vk.com/id398982326?profile=1",
    "#category": ("", "vk", "photos"),
    "#class"   : vk.VkPhotosExtractor,
},

{
    "#url"     : "https://vk.com/albums-165740836",
    "#category": ("", "vk", "photos"),
    "#class"   : vk.VkPhotosExtractor,
},

{
    "#url"     : "https://vk.com/album-165740836_281339889",
    "#category": ("", "vk", "album"),
    "#class"   : vk.VkAlbumExtractor,
    "#count"   : 12,
},

{
    "#url"     : "https://vk.com/album-53775183_00",
    "#comment" : "'Access denied' (#2556)",
    "#category": ("", "vk", "album"),
    "#class"   : vk.VkAlbumExtractor,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://vk.com/album232175027_00",
    "#category": ("", "vk", "album"),
    "#class"   : vk.VkAlbumExtractor,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://vk.com/tag304303884",
    "#category": ("", "vk", "tagged"),
    "#class"   : vk.VkTaggedExtractor,
    "#count"   : 44,
},

)
