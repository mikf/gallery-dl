# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import artstation
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.artstation.com/sungchoi/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
    "#pattern" : r"https://\w+\.artstation\.com/p/assets/images/images/\d+/\d+/\d+/(4k|large|medium|small)/[^/]+",
    "#range"   : "1-10",
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.artstation.com/sungchoi/albums/all/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://sungchoi.artstation.com/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://sungchoi.artstation.com/projects/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://www.artstation.com/huimeiye/albums/770899",
    "#category": ("", "artstation", "album"),
    "#class"   : artstation.ArtstationAlbumExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://www.artstation.com/huimeiye/albums/770898",
    "#category": ("", "artstation", "album"),
    "#class"   : artstation.ArtstationAlbumExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://huimeiye.artstation.com/albums/770899",
    "#category": ("", "artstation", "album"),
    "#class"   : artstation.ArtstationAlbumExtractor,
},

{
    "#url"     : "https://www.artstation.com/mikf/likes",
    "#category": ("", "artstation", "likes"),
    "#class"   : artstation.ArtstationLikesExtractor,
    "#pattern" : r"https://\w+\.artstation\.com/p/assets/images/images/\d+/\d+/\d+/(4k|large|medium|small)/[^/]+",
    "#count"   : 6,
},

{
    "#url"     : "https://www.artstation.com/mikf/collections/2647023",
    "#category": ("", "artstation", "collection"),
    "#class"   : artstation.ArtstationCollectionExtractor,
    "#count"   : 10,

    "collection": {
        "id"            : 2647023,
        "is_private"    : False,
        "name"          : "テスト",
        "projects_count": 3,
        "user_id"       : 697975,
        "active_projects_count" : 3,
        "micro_square_image_url": "https://cdna.artstation.com/p/assets/images/images/005/131/434/micro_square/gaeri-kim-cat-front.jpg?1488720625",
        "small_square_image_url": "https://cdna.artstation.com/p/assets/images/images/005/131/434/small_square/gaeri-kim-cat-front.jpg?1488720625",
    },
    "user": "mikf",
},

{
    "#url"     : "https://www.artstation.com/mikf/collections",
    "#category": ("", "artstation", "collections"),
    "#class"   : artstation.ArtstationCollectionsExtractor,
    "#results" : (
        "https://www.artstation.com/mikf/collections/2647023",
        "https://www.artstation.com/mikf/collections/2647719",
    ),

    "id"            : range(2647023, 2647719),
    "is_private"    : False,
    "name"          : r"re:テスト|empty",
    "projects_count": int,
    "user_id"       : 697975,
    "active_projects_count" : int,
    "micro_square_image_url": str,
    "small_square_image_url": str,
},

{
    "#url"     : "https://www.artstation.com/sungchoi/likes",
    "#comment" : "no likes",
    "#category": ("", "artstation", "likes"),
    "#class"   : artstation.ArtstationLikesExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.artstation.com/contests/thu-2017/challenges/20",
    "#category": ("", "artstation", "challenge"),
    "#class"   : artstation.ArtstationChallengeExtractor,
},

{
    "#url"     : "https://www.artstation.com/contests/beyond-human/challenges/23?sorting=winners",
    "#category": ("", "artstation", "challenge"),
    "#class"   : artstation.ArtstationChallengeExtractor,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://www.artstation.com/search?query=ancient&sort_by=rank",
    "#category": ("", "artstation", "search"),
    "#class"   : artstation.ArtstationSearchExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.artstation.com/artwork?sorting=latest",
    "#category": ("", "artstation", "artwork"),
    "#class"   : artstation.ArtstationArtworkExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.artstation.com/artwork/LQVJr",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#pattern"     : r"https?://\w+\.artstation\.com/p/assets/images/images/008/760/279/4k/.+",
    "#sha1_content": "3f211ce0d6ecdb502db2cdf7bbeceb11d8421170",
},

{
    "#url"     : "https://www.artstation.com/artwork/Db3dy",
    "#comment" : "multiple images per project",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.artstation.com/artwork/lR8b5k",
    "#comment" : "artstation video clips (#2566)",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#options" : {"videos": True},
    "#range"   : "2-3",
    "#results" : (
        "https://cdn.artstation.com/p/video_sources/000/819/843/infection-4.mp4",
        "https://cdn.artstation.com/p/video_sources/000/819/725/infection-veinonly-2.mp4",
    ),
},

{
    "#url"     : "https://www.artstation.com/artwork/r8zRm",
    "#comment" : "mview embeds (#2566)",
    "#class"   : artstation.ArtstationImageExtractor,
    "#options" : {"mviews": True},
    "#range"   : "4",
    "#results" : (
        "https://cdna.artstation.com/p/assets/marmosets/attachments/010/915/068/original/Orca-MarmosetViewer.mview?1526922111",
    ),

    "extension": "mview",
},

{
    "#url"     : "https://www.artstation.com/artwork/g4WPK",
    "#comment" : "embedded youtube video",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#options" : {"external": True},
    "#pattern" : r"ytdl:https://www\.youtube(-nocookie)?\.com/embed/JNFfJtwwrU0",
    "#range"   : "2",
},

{
    "#url"     : "https://www.artstation.com/artwork/3q3mXB",
    "#comment" : "404 (#3016)",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://sungchoi.artstation.com/projects/LQVJr",
    "#comment" : "alternate URL patterns",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://artstn.co/p/LQVJr",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://www.artstation.com/sungchoi/following",
    "#category": ("", "artstation", "following"),
    "#class"   : artstation.ArtstationFollowingExtractor,
    "#pattern" : artstation.ArtstationUserExtractor.pattern,
    "#count"   : ">= 40",
},

{
    "#url"     : "https://fede-x-rojas.artstation.com/projects/WBdaZy",
    "#comment" : "dash in username",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://fede-x-rojas.artstation.com/albums/8533110",
    "#comment" : "dash in username",
    "#category": ("", "artstation", "album"),
    "#class"   : artstation.ArtstationAlbumExtractor,
},

{
    "#url"     : "https://fede-x-rojas.artstation.com/",
    "#comment" : "dash in username",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
},

)
