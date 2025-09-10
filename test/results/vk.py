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
    "date": "type:datetime",
    "user": {
        "group": False,
        "id"  : "398982326",
        "info": "Мы за Движуху! – m1ni SounD #4 [EROmusic]",
        "name": "id398982326",
        "nick": "Dobrov Kurva",
    },
},

{
    "#url"     : "https://vk.com/cosplayinrussia",
    "#category": ("", "vk", "photos"),
    "#class"   : vk.VkPhotosExtractor,
    "#range"   : "15-25",

    "id"  : r"re:\d+",
    "date": "type:datetime",
    "user": {
        "group": True,
        "id"  : "-165740836",
        "info": "",
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

    "date": "type:datetime",
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
    "#log"     : "-165740836_281339889: Failed to extract metadata ('Access denied')",

    "album": {
        "id"    : "281339889",
        "!name" : str,
        "!count": int,
    },
    "user": {
        "id": "-165740836",
        "!name" : str,
        "!nick" : str,
        "!group": bool,

    },
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
    "#url"     : "https://vk.com/album-205150448_00",
    "#class"   : vk.VkAlbumExtractor,
    "#range"   : "1-25",
    "#count"   : 25,

    "id"           : r"re:\d+",
    "width"        : range(100, 8_000),
    "height"       : range(100, 8_000),
    "filename"     : str,
    "extension"    : {"jpg", "png"},
    "date"         : "type:datetime",
    "count"        : 826,
    "num"          : range(1, 25),
    "description"  : str,
    "hash"         : r"re:[0-9a-f]{18}",
    "likes"        : int,
    "album"        : {
        "id"   : "00",
        "name" : "Community wall photos",
        "count": 826,
    },
    "user"         : {
        "id"   : "-205150448",
        "name" : "otjareniy",
        "nick" : "Отжареный Овощ(16+)",
        "group": True,
    },
},

{
    "#url"     : "https://vk.com/tag304303884",
    "#category": ("", "vk", "tagged"),
    "#class"   : vk.VkTaggedExtractor,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://vk.com/wall-213352498_2115",
    "#class"   : vk.VkWallPostExtractor,
    "#results" : (
        "https://sun9-42.userapi.com/s/v1/ig2/53qxcL7M8408L2HNDTHdHz-HXbprXBn1BLbE5HTuj-OsZD4I483jtZb8yMk9Mr4zzfPJhqBIJlAprWVhIqlk4Fn4.jpg?quality=95&as=32x57,48x85,72x128,108x192,160x284,240x427,360x640,480x853,540x960,640x1138,720x1280&from=bu&cs=720x0",
        "https://sun9-49.userapi.com/s/v1/ig2/FnvT8T3mC2yQWc5yJTOe25Kj864ohqvTgOcTudqrE4sPfCMexS1mzNmgUndgxUbqhht-YmIVKW_edDFtzCLXzf7h.jpg?quality=95&as=32x57,48x85,72x128,108x192,160x284,240x427,360x640,480x853,540x960,640x1138,720x1280&from=bu&cs=720x0",
        "https://sun9-78.userapi.com/s/v1/ig2/6VB0Cnmdtb9rDNFd5iHv5QJAJ-y-xSVELEoCLlOf_ej2BWVf61G3DSXbnXgmx-QFtQkOOnHIhCLFFLTIFKeVBR5Q.jpg?quality=95&as=32x57,48x85,72x128,108x192,160x284,240x427,360x640,480x853,540x960,640x1138,720x1280&from=bu&cs=720x0",
        "https://sun9-60.userapi.com/s/v1/ig2/KO5SzdRUHjZRKlHii4oJ4BrTo5nbdyP3CCpf6_RfHhrEIx6jiVPlWH1R--fpoK5-0rigqXuaG68q39m5VQVy6YFo.jpg?quality=95&as=32x57,48x85,72x128,108x192,160x284,240x427,360x640,480x853,540x960,640x1138,720x1280&from=bu&cs=720x0",
        "https://sun9-33.userapi.com/s/v1/ig2/IAN1ZHmVVtjRj0U7wGAfnMc5Xp83EFFYZAVqNgMKpfthLHOe6wh0bodM_xDwIALvVl4pcZ66Fv3bOROG4sUTwY21.jpg?quality=95&as=32x57,48x85,72x128,108x192,160x284,240x427,360x640,480x853,540x960,640x1138,720x1280&from=bu&cs=720x0",
        "https://sun9-44.userapi.com/s/v1/ig2/RLzDGnlmu7C0sLh2YI2R4L9RBgZ061QLOsxogjEtC0cBZJ9HvhNwe1V16QX0tNLkTOLELAp8JDHwOo6dMvoWydeh.jpg?quality=95&as=32x57,48x85,72x128,108x192,160x284,240x427,360x640,480x853,540x960,640x1138,720x1280&from=bu&cs=720x0",
    ),

    "id"           : r"re:^\d+$",
    "width"        : 720,
    "height"       : 1280,
    "count"        : 6,
    "num"          : range(1, 6),
    "likes"        : int,
    "user"         : {
        "id": "-213352498",
    },
    "wall"         : {
        "description": "🎄 Обновляем не только аватарки, но и обои на телефоне",
        "id"         : "2115",
    },
},

)
