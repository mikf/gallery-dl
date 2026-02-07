# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import artstation


__tests__ = (
{
    "#url"     : "https://www.artstation.com/sungchoi/",
    "#class"   : artstation.ArtstationUserExtractor,
    "#pattern" : r"https://\w+\.artstation\.com/p/assets/images/images/\d+/\d+/\d+/8k/[^/]+",
    "#range"   : "1-10",
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.artstation.com/sungchoi/albums/all/",
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://sungchoi.artstation.com/",
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://sungchoi.artstation.com/projects/",
    "#comment" : "alternate user URL format",
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://www.artstation.com/huimeiye/albums/770899",
    "#comment" : "'Hellboy' album",
    "#class"   : artstation.ArtstationAlbumExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://www.artstation.com/huimeiye/albums/770898",
    "#comment" : "non-existent album",
    "#class"   : artstation.ArtstationAlbumExtractor,
    "#exception": "NotFoundError",
},

{
    "#url"     : "https://huimeiye.artstation.com/albums/770899",
    "#comment" : "alternate user URL format",
    "#class"   : artstation.ArtstationAlbumExtractor,
},

{
    "#url"     : "https://www.artstation.com/mikf/likes",
    "#class"   : artstation.ArtstationLikesExtractor,
    "#pattern" : r"https://\w+\.artstation\.com/p/assets/images/images/\d+/\d+/\d+/8k/[^/]+",
    "#count"   : 6,
},

{
    "#url"     : "https://www.artstation.com/mikf/collections/2647023",
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
    "#class"   : artstation.ArtstationLikesExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.artstation.com/contests/thu-2017/challenges/20",
    "#class"   : artstation.ArtstationChallengeExtractor,
},

{
    "#url"     : "https://www.artstation.com/challenges/beyond-human/categories/23/submissions",
    "#class"   : artstation.ArtstationChallengeExtractor,
},

{
    "#url"     : "https://www.artstation.com/contests/beyond-human/challenges/23?sorting=popular",
    "#class"   : artstation.ArtstationChallengeExtractor,
    "#range"   : "1-30",
    "#count"   : 30,

    "challenge": {
        "id"        : 23,
        "headline"  : "Imagining Where Future Humans Live",
        "created_at": "2017-06-26T14:45:43+00:00",
        "contest"   : {
            "archived" : True,
            "published": True,
            "slug"     : "beyond-human",
            "title"    : "Beyond Human",
            "submissions_count": 4258,
        },
    },
},

{
    "#url"     : "https://www.artstation.com/search?query=ancient&sort_by=rank",
    "#class"   : artstation.ArtstationSearchExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.artstation.com/artwork?sorting=latest",
    "#class"   : artstation.ArtstationArtworkExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.artstation.com/artwork/LQVJr",
    "#class"   : artstation.ArtstationImageExtractor,
    "#pattern"     : r"https?://\w+\.artstation\.com/p/assets/images/images/008/760/279/8k/.+",
    "#sha1_content": "3f211ce0d6ecdb502db2cdf7bbeceb11d8421170",
},

{
    "#url"     : "https://www.artstation.com/artwork/Db3dy",
    "#comment" : "multiple images per project",
    "#class"   : artstation.ArtstationImageExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.artstation.com/artwork/lR8b5k",
    "#comment" : "artstation video clips (#2566)",
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
    "#class"   : artstation.ArtstationImageExtractor,
    "#options" : {"external": True},
    "#pattern" : r"ytdl:https://www\.youtube(-nocookie)?\.com/embed/JNFfJtwwrU0",
    "#range"   : "2",
},

{
    "#url"     : "https://www.artstation.com/artwork/3q3mXB",
    "#comment" : "404 (#3016)",
    "#class"   : artstation.ArtstationImageExtractor,
    "#exception": "NotFoundError",
},

{
    "#url"     : "https://sungchoi.artstation.com/projects/LQVJr",
    "#comment" : "alternate URL patterns",
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://artstn.co/p/LQVJr",
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://www.artstation.com/sungchoi/following",
    "#class"   : artstation.ArtstationFollowingExtractor,
    "#pattern" : artstation.ArtstationUserExtractor.pattern,
    "#count"   : ">= 40",
},

{
    "#url"     : "https://fede-x-rojas.artstation.com/projects/WBdaZy",
    "#comment" : "dash in username",
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://fede-x-rojas.artstation.com/albums/8533110",
    "#comment" : "dash in username",
    "#class"   : artstation.ArtstationAlbumExtractor,
},

{
    "#url"     : "https://fede-x-rojas.artstation.com/",
    "#comment" : "dash in username",
    "#class"   : artstation.ArtstationUserExtractor,
},

)
