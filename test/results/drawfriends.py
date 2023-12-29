# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v01


__tests__ = (
{
    "#url"     : "https://drawfriends.booru.org/index.php?page=post&s=list&tags=all",
    "#category": ("gelbooru_v01", "drawfriends", "tag"),
    "#class"   : gelbooru_v01.GelbooruV01TagExtractor,
},

{
    "#url"     : "https://drawfriends.booru.org/index.php?page=favorites&s=view&id=1",
    "#category": ("gelbooru_v01", "drawfriends", "favorite"),
    "#class"   : gelbooru_v01.GelbooruV01FavoriteExtractor,
},

{
    "#url"     : "https://drawfriends.booru.org/index.php?page=post&s=view&id=107474",
    "#category": ("gelbooru_v01", "drawfriends", "post"),
    "#class"   : gelbooru_v01.GelbooruV01PostExtractor,
},

)
