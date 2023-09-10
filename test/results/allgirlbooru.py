# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v01


__tests__ = (
{
    "#url"     : "https://allgirl.booru.org/index.php?page=post&s=list&tags=dress",
    "#category": ("gelbooru_v01", "allgirlbooru", "tag"),
    "#class"   : gelbooru_v01.GelbooruV01TagExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "https://allgirl.booru.org/index.php?page=favorites&s=view&id=380",
    "#category": ("gelbooru_v01", "allgirlbooru", "favorite"),
    "#class"   : gelbooru_v01.GelbooruV01FavoriteExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://allgirl.booru.org/index.php?page=post&s=view&id=107213",
    "#category": ("gelbooru_v01", "allgirlbooru", "post"),
    "#class"   : gelbooru_v01.GelbooruV01PostExtractor,
    "#sha1_url"    : "b416800d2d2b072f80d3b37cfca9cb806fb25d51",
    "#sha1_content": "3e3c65e0854a988696e11adf0de52f8fa90a51c7",

    "created_at": "2021-02-13 16:27:39",
    "date"      : "dt:2021-02-13 16:27:39",
    "file_url"  : "https://img.booru.org/allgirl//images/107/2aaa0438d58fc7baa75a53b4a9621bb89a9d3fdb.jpg",
    "height"    : "1200",
    "id"        : "107213",
    "md5"       : "2aaa0438d58fc7baa75a53b4a9621bb89a9d3fdb",
    "rating"    : "s",
    "score"     : str,
    "source"    : "",
    "tags"      : "blush dress green_eyes green_hair hatsune_miku long_hair twintails vocaloid",
    "uploader"  : "Honochi31",
    "width"     : "1600",
},

)
