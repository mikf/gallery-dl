# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import luscious
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://luscious.net/albums/okinami-no-koigokoro_277031/",
    "#category": ("", "luscious", "album"),
    "#class"   : luscious.LusciousAlbumExtractor,
    "#pattern" : r"https://storage\.bhs\.cloud\.ovh\.net/v1/AUTH_\w+/images/NTRshouldbeillegal/277031/luscious_net_\d+_\d+\.jpg$",

    "album"           : {
        "__typename"                 : "Album",
        "audiences"                  : list,
        "content"                    : "Hentai",
        "cover"                      : str,
        "created"                    : 1479625853,
        "created_by"                 : "Hive Mind",
        "date"                       : "dt:2016-11-20 07:10:53",
        "description"                : "Enjoy.",
        "download_url"               : "/download/r/25/277031/",
        "genres"                     : list,
        "id"                         : 277031,
        "is_manga"                   : True,
        "labels"                     : list,
        "language"                   : "English",
        "like_status"                : "none",
        "modified"                   : int,
        "permissions"                : list,
        "rating"                     : None,
        "slug"                       : "okinami-no-koigokoro",
        "status"                     : None,
        "tags"                       : list,
        "title"                      : "Okinami no Koigokoro",
        "url"                        : "/albums/okinami-no-koigokoro_277031/",
        "marked_for_deletion"        : False,
        "marked_for_processing"      : False,
        "number_of_animated_pictures": 0,
        "number_of_favorites"        : int,
        "number_of_pictures"         : 18,
    },
    "aspect_ratio"    : r"re:\d+:\d+",
    "category"        : "luscious",
    "created"         : int,
    "date"            : "type:datetime",
    "height"          : int,
    "id"              : int,
    "is_animated"     : False,
    "like_status"     : "none",
    "position"        : int,
    "resolution"      : r"re:\d+x\d+",
    "status"          : None,
    "tags"            : list,
    "thumbnail"       : str,
    "title"           : str,
    "width"           : int,
    "number_of_comments": int,
    "number_of_favorites": int,
},

{
    "#url"     : "https://luscious.net/albums/not-found_277035/",
    "#category": ("", "luscious", "album"),
    "#class"   : luscious.LusciousAlbumExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://members.luscious.net/albums/login-required_323871/",
    "#category": ("", "luscious", "album"),
    "#class"   : luscious.LusciousAlbumExtractor,
    "#count"   : 64,
},

{
    "#url"     : "https://www.luscious.net/albums/okinami_277031/",
    "#category": ("", "luscious", "album"),
    "#class"   : luscious.LusciousAlbumExtractor,
},

{
    "#url"     : "https://members.luscious.net/albums/okinami_277031/",
    "#category": ("", "luscious", "album"),
    "#class"   : luscious.LusciousAlbumExtractor,
},

{
    "#url"     : "https://luscious.net/pictures/c/video_game_manga/album/okinami-no-koigokoro_277031/sorted/position/id/16528978/@_1",
    "#category": ("", "luscious", "album"),
    "#class"   : luscious.LusciousAlbumExtractor,
},

{
    "#url"     : "https://members.luscious.net/albums/list/",
    "#category": ("", "luscious", "search"),
    "#class"   : luscious.LusciousSearchExtractor,
},

{
    "#url"     : "https://members.luscious.net/albums/list/?display=date_newest&language_ids=%2B1&tagged=+full_color&page=1",
    "#category": ("", "luscious", "search"),
    "#class"   : luscious.LusciousSearchExtractor,
    "#pattern" : luscious.LusciousAlbumExtractor.pattern,
    "#range"   : "41-60",
    "#count"   : 20,
},

)
