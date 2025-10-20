# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import inkbunny


__tests__ = (
{
    "#url"     : "https://inkbunny.net/soina",
    "#category": ("", "inkbunny", "user"),
    "#class"   : inkbunny.InkbunnyUserExtractor,
    "#pattern" : r"https://[\w.]+\.metapix\.net/files/full/\d+/\d+_soina_.+",
    "#range"   : "20-50",

    "date"           : "type:datetime",
    "deleted"        : bool,
    "file_id"        : r"re:[0-9]+",
    "filename"       : r"re:[0-9]+_soina_\w+",
    "full_file_md5"  : r"re:[0-9a-f]{32}",
    "mimetype"       : str,
    "submission_id"  : r"re:[0-9]+",
    "user_id"        : "20969",
    "comments_count" : r"re:[0-9]+",
    "favorite"       : bool,
    "favorites_count": r"re:[0-9]+",
    "friends_only"   : bool,
    "guest_block"    : bool,
    "hidden"         : bool,
    "pagecount"      : r"re:[0-9]+",
    "pools"          : list,
    "pools_count"    : int,
    "public"         : bool,
    "rating_id"      : r"re:[0-9]+",
    "rating_name"    : str,
    "ratings"        : list,
    "scraps"         : bool,
    "tags"           : list,
    "title"          : str,
    "type_name"      : str,
    "username"       : "soina",
    "views"          : str,
},

{
    "#url"     : "https://inkbunny.net/gallery/soina",
    "#category": ("", "inkbunny", "gallery"),
    "#class"   : inkbunny.InkbunnyUserExtractor,
    "#range"   : "1-25",

    "scraps": False,
},

{
    "#url"     : "https://inkbunny.net/scraps/soina",
    "#category": ("", "inkbunny", "scraps"),
    "#class"   : inkbunny.InkbunnyUserExtractor,
    "#range"   : "1-25",

    "scraps": True,
},

{
    "#url"     : "https://inkbunny.net/poolview_process.php?pool_id=28985",
    "#category": ("", "inkbunny", "pool"),
    "#class"   : inkbunny.InkbunnyPoolExtractor,
    "#count"   : 9,

    "pool_id": "28985",
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?rid=ffffffffff&mode=pool&pool_id=28985&page=1&orderby=pool_order&random=no",
    "#category": ("", "inkbunny", "pool"),
    "#class"   : inkbunny.InkbunnyPoolExtractor,
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?mode=pool&pool_id=28985",
    "#category": ("", "inkbunny", "pool"),
    "#class"   : inkbunny.InkbunnyPoolExtractor,
},

{
    "#url"     : "https://inkbunny.net/userfavorites_process.php?favs_user_id=20969",
    "#category": ("", "inkbunny", "favorite"),
    "#class"   : inkbunny.InkbunnyFavoriteExtractor,
    "#pattern" : r"https://[\w.]+\.metapix\.net/files/full/\d+/\d+_\w+_.+",
    "#range"   : "20-50",

    "favs_user_id" : "20969",
    "favs_username": "soina",
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?rid=ffffffffff&mode=userfavs&random=no&orderby=fav_datetime&page=1&user_id=20969",
    "#category": ("", "inkbunny", "favorite"),
    "#class"   : inkbunny.InkbunnyFavoriteExtractor,
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?mode=userfavs&user_id=20969",
    "#category": ("", "inkbunny", "favorite"),
    "#class"   : inkbunny.InkbunnyFavoriteExtractor,
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?rid=ffffffffff&mode=unreadsubs&page=1&orderby=unread_datetime",
    "#category": ("", "inkbunny", "unread"),
    "#class"   : inkbunny.InkbunnyUnreadExtractor,
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?mode=unreadsubs",
    "#category": ("", "inkbunny", "unread"),
    "#class"   : inkbunny.InkbunnyUnreadExtractor,
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?rid=ffffffffff&mode=search&page=1&orderby=create_datetime&text=cute&stringtype=and&keywords=yes&title=yes&description=no&artist=&favsby=&type=&days=&keyword_id=&user_id=&random=&md5=",
    "#category": ("", "inkbunny", "search"),
    "#class"   : inkbunny.InkbunnySearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,

    "search": {
        "rid"        : "ffffffffff",
        "mode"       : "search",
        "page"       : "1",
        "orderby"    : "create_datetime",
        "text"       : "cute",
        "stringtype" : "and",
        "keywords"   : "yes",
        "title"      : "yes",
        "description": "no",
    },
},

{
    "#url"     : "https://inkbunny.net/submissionsviewall.php?mode=search",
    "#category": ("", "inkbunny", "search"),
    "#class"   : inkbunny.InkbunnySearchExtractor,
},

{
    "#url"     : "https://inkbunny.net/watchlist_process.php?mode=watching&user_id=20969",
    "#category": ("", "inkbunny", "following"),
    "#class"   : inkbunny.InkbunnyFollowingExtractor,
    "#pattern" : inkbunny.InkbunnyUserExtractor.pattern,
    "#count"   : ">= 90",
},

{
    "#url"     : "https://inkbunny.net/usersviewall.php?rid=ffffffffff&mode=watching&page=1&user_id=20969&orderby=added&namesonly=",
    "#category": ("", "inkbunny", "following"),
    "#class"   : inkbunny.InkbunnyFollowingExtractor,
},

{
    "#url"     : "https://inkbunny.net/usersviewall.php?mode=watching&user_id=20969",
    "#category": ("", "inkbunny", "following"),
    "#class"   : inkbunny.InkbunnyFollowingExtractor,
},

{
    "#url"     : "https://inkbunny.net/s/1829715",
    "#category": ("", "inkbunny", "post"),
    "#class"   : inkbunny.InkbunnyPostExtractor,
    "#pattern"     : r"https://[\w.]+\.metapix\.net/files/full/2626/2626843_soina_dscn2296\.jpg",
    "#sha1_content": "cf69d8dddf0822a12b4eef1f4b2258bd600b36c8",
},

{
    "#url"     : "https://inkbunny.net/s/2044094",
    "#category": ("", "inkbunny", "post"),
    "#class"   : inkbunny.InkbunnyPostExtractor,
    "#count"   : 4,
},

)
