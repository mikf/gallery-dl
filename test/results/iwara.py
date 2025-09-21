# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import iwara


__tests__ = (
{
    "#url"          : "https://www.iwara.tv/profile/user2426993",
    "#class"        : iwara.IwaraUserExtractor,
    "#results"      : (
        "https://www.iwara.tv/profile/user2426993/images",
        "https://www.iwara.tv/profile/user2426993/videos",
    ),
},

{
    "#url"          : "https://www.iwara.tv/profile/user2426993/images",
    "#class"        : iwara.IwaraUserImagesExtractor,
    "#results"      : (
        "https://i.iwara.tv/image/original/215ef6c5-47a9-4894-aaef-7bbc7ed2b5d0/215ef6c5-47a9-4894-aaef-7bbc7ed2b5d0.png",
        "https://i.iwara.tv/image/original/382ce6bc-0393-43dd-adb7-dfd514a72011/382ce6bc-0393-43dd-adb7-dfd514a72011.png",
        "https://i.iwara.tv/image/original/57fad542-d5c7-4671-b295-f7c4886db80e/57fad542-d5c7-4671-b295-f7c4886db80e.png",
        "https://i.iwara.tv/image/original/80b61308-08b5-469b-ab86-b2d1a9819a32/80b61308-08b5-469b-ab86-b2d1a9819a32.png",
    ),

    "extension": "png",
    "type"     : "image",
    "count"    : 1,
    "num"      : 1,
},

{
    "#url"          : "https://www.iwara.tv/profile/user2426993/videos",
    "#class"        : iwara.IwaraUserVideosExtractor,
    "#pattern"      : (
        r"https://\w+.iwara.tv/download\?filename=8035c1cb-6ac6-45df-a171-4d981a8339c5_Source.mp4&path=2025%2F07%2F04&expires=\d+.+",
        r"https://\w+.iwara.tv/download\?filename=59691a5b-dd5d-4476-919d-dc0d8c9ee11f_Source.mp4&path=2025%2F06%2F21&expires=\d+.+",
    ),

    "extension": "mp4",
    "type"     : "video",
    "count"    : 1,
    "num"      : 1,
},

{
    "#url"          : "https://www.iwara.tv/profile/tyron82/playlists",
    "#class"        : iwara.IwaraUserPlaylistsExtractor,
    "#pattern"      : iwara.IwaraPlaylistExtractor.pattern,
    "#count"        : range(10, 20),

    "type"          : "playlist",
},

{
    "#url"          : "https://www.iwara.tv/profile/tyron82/following",
    "#class"        : iwara.IwaraFollowingExtractor,
    "#pattern"      : iwara.IwaraUserExtractor.pattern,
    "#range"        : "1-100",
    "#count"        : 100,

    "type"          : "user",
},

{
    "#url"          : "https://www.iwara.tv/profile/tyron82/followers",
    "#class"        : iwara.IwaraFollowersExtractor,
    "#pattern"      : iwara.IwaraUserExtractor.pattern,
    "#range"        : "1-100",
    "#count"        : 100,

    "type"          : "user",
},

{
    "#url"          : "https://www.iwara.tv/playlist/01ea603a-4e70-4a36-bc28-dc717eebc2d7",
    "#category"     : ("", "iwara", "playlist"),
    "#class"        : iwara.IwaraPlaylistExtractor,
    "#pattern"      : r"https://\w+.iwara.tv/download\?filename=b7708020-f531-4eb4-bfd3-c62f3d17927e_Source.mp4&path=2024%2F05%2F12&.+",
    "#count"        : 1,

    "id"            : "OaoVL8nqijDjhB",
    "title"         : "MMD.RuanMei's body modification",
    "file_id"       : "b7708020-f531-4eb4-bfd3-c62f3d17927e",
    "filename"      : "b7708020-f531-4eb4-bfd3-c62f3d17927e",
    "extension"     : "mp4",
    "mime"          : "video/mp4",
    "size"          : 225197782,
    "width"         : None,
    "height"        : None,
    "duration"      : 654,
    "type"          : "video",
    "user"          : {
        "date"       : "dt:2020-05-15 09:59:32",
        "description": str,
        "id"         : "c9a08dd5-3cb5-4d7c-b9bb-9eb4c55eda14",
        "name"       : "arisananades",
        "nick"       : "Arisananades",
        "premium"    : False,
        "role"       : "user",
        "status"     : "active",
    },
},

{
    "#url"          : "https://www.iwara.tv/favorites/videos",
    "#class"        : iwara.IwaraFavoriteExtractor,
    "#auth"         : True,
},

{
    "#url"          : "https://www.iwara.tv/favorites/images",
    "#class"        : iwara.IwaraFavoriteExtractor,
    "#auth"         : True,
},

{
    "#url"          : "https://www.iwara.tv/search?query=genshin%20tentacle&type=video",
    "#category"     : ("", "iwara", "search"),
    "#class"        : iwara.IwaraSearchExtractor,
    "#count"        : 5,

    "extension"     : "mp4",
    "mime"          : "video/mp4",
    "width"         : None,
    "height"        : None,
    "type"          : "video",
    "user": {
        "date"       : "dt:2022-01-12 17:08:38",
        "description": str,
        "id"         : "3ec40862-bcb6-4c2e-9f3b-6da3a00cc2d9",
        "name"       : "nizipaco-kyu",
        "nick"       : "Nizipaco - Kyu",
        "premium"    : False,
        "role"       : "user",
        "status"     : "active",
    },
},

{
    "#url"          : "https://www.iwara.tv/search?query=genshin%20layla%20sex&type=image",
    "#category"     : ("", "iwara", "search"),
    "#class"        : iwara.IwaraSearchExtractor,
    "#count"        : 20,

    "duration"      : None,
    "type"          : "image",
},

{
    "#url"          : "https://www.iwara.tv/videos?tags=aether%2Ccitlali",
    "#category"     : ("", "iwara", "tag"),
    "#class"        : iwara.IwaraTagExtractor,
    "#pattern"      : (
        r"https://\w+.iwara.tv/download\?filename=d8e3735d-048c-4525-adcf-4265c8b45444_Source.mp4&path=2025%2F05%2F15&expires=\d+&.+",
        r"https://\w+.iwara.tv/download\?filename=cc1a1aba-10b9-4e0f-a20f-5b9b17b33db1_Source.mp4&path=2025%2F04%2F03&expires=\d+&.+",
        r"https://\w+.iwara.tv/download\?filename=94a8a1b9-7586-4771-accd-6f9cb4c6a5a1_Source.mp4&path=2025%2F03%2F21&expires=\d+&.+",
    ),

    "user": {
        "id"  : "2b4391f3-c46f-43f9-b18f-8bdb8a9df74f",
        "name": "lenoria",
        "nick": "lenoria",
    },
    "extension"     : "mp4",
    "mime"          : "video/mp4",
    "width"         : None,
    "height"        : None,
    "type"          : "video",
    "search_tags"   : "aether,citlali",
    "duration"      : range(90, 200),
},

{
    "#url"          : "https://www.iwara.tv/images?tags=genshin_impact%2Ccitlali",
    "#category"     : ("", "iwara", "tag"),
    "#class"        : iwara.IwaraTagExtractor,
    "#pattern"      : r"https://i.iwara.tv/image/original/[0-9a-f-]{36}/[0-9a-f-]{36}\.(jpg|png|webm)",

    "duration"    : None,
    "extension"   : {"jpg", "png", "webm"},
    "mime"        : {"image/jpeg", "image/png", "video/webm"},
    "search_tags" : "genshin_impact,citlali",
    "type"        : "image",
},

{
    "#url"        : "https://www.iwara.tv/video/6QvQvzZnELJ9vv/bluearchive-rio",
    "#category"   : ("", "iwara", "video"),
    "#class"      : iwara.IwaraVideoExtractor,
    "#pattern"    : r"https://\w+.iwara.tv/download\?filename=7ba6e734-b9df-4588-88fc-4eef2bbf5c56_Source.mp4&path=2025%2F07%2F05&expires=\d+&hash=[0-9a-f]{64}",
    "#count"      : 1,

    "comments"    : range(100, 200),
    "count"       : 1,
    "date"        : "dt:2025-07-05 06:49:56",
    "date_updated": "dt:2025-07-05 06:50:14",
    "duration"    : 107,
    "extension"   : "mp4",
    "file_id"     : "7ba6e734-b9df-4588-88fc-4eef2bbf5c56",
    "filename"    : "7ba6e734-b9df-4588-88fc-4eef2bbf5c56",
    "height"      : None,
    "id"          : "6QvQvzZnELJ9vv",
    "likes"       : range(8_000, 15_000),
    "mime"        : "video/mp4",
    "num"         : 1,
    "rating"      : "ecchi",
    "size"        : 86328642,
    "slug"        : "bluearchive-rio",
    "title"       : "[BlueArchive / ブルアカ] Rio",
    "type"        : "video",
    "views"       : range(200_000, 500_000),
    "width"       : None,
    "description" : """\
You can find FHD(1080p) and UHD(2160p) videos on my patreon page, so please check that out if you are interested.

Patreon : https://www.patreon.com/croove
Twitter : https://x.com/croove_nsfw\
""",
    "tags"        : [
        "blender",
        "blue_archive",
        "tsukatsuki_rio",
    ],
    "user"        : {
        "date"       : "dt:2022-04-01 01:55:59",
        "id"         : "b3f86af1-874c-41f1-b62e-4e4b736ad3a4",
        "name"       : "croove",
        "nick"       : "crooveNSFW",
        "premium"    : False,
        "role"       : "user",
        "status"     : "active",
        "description": """\
You can find FHD(1080p) and UHD(2160p) videos on my patreon page, so please check that out if you are interested.

Patreon : https://www.patreon.com/croove
Twitter : https://x.com/croove_nsfw\
""",
    },
},

{
    "#url"        : "https://www.iwara.tv/image/5m3gLfcei6BQsL/sparkle",
    "#category"   : ("", "iwara", "image"),
    "#class"      : iwara.IwaraImageExtractor,
    "#pattern"    : r"https://i.iwara.tv/image/original/[\w-]{36}/[\w-]{36}\.png",
    "#count"      : 13,

    "comments"    : int,
    "count"       : 13,
    "date"        : "type:datetime",
    "date_updated": "type:datetime",
    "description" : "card from OoOoO & Rat",
    "duration"    : None,
    "extension"   : "png",
    "file_id"     : "iso:uuid",
    "filename"    : "iso:uuid",
    "height"      : int,
    "width"       : int,
    "size"        : int,
    "id"          : "5m3gLfcei6BQsL",
    "likes"       : int,
    "mime"        : "image/png",
    "num"         : range(1, 13),
    "rating"      : "ecchi",
    "slug"        : "sparkle",
    "title"       : "Sparkle",
    "type"        : "image",
    "views"       : int,
    "tags"        : [
        "koikatsu",
        "sparkle",
    ],
    "user"        : {
        "date"       : "dt:2025-07-04 19:17:20",
        "description": "card from OoOoO & Rat",
        "id"         : "771d2b29-5935-43d7-85e1-30abbf47ccad",
        "name"       : "zcccz",
        "nick"       : "zcccz",
        "premium"    : False,
        "role"       : "limited",
        "status"     : "active",
    },
},

{
    "#url"          : "https://www.iwara.tv/image/PbYJb57QqwrFp0",
    "#category"     : ("", "iwara", "image"),
    "#class"        : iwara.IwaraImageExtractor,
    "#results"      : "https://i.iwara.tv/image/original/0302deee-9cd5-4c1f-b931-04caf329c0c7/0302deee-9cd5-4c1f-b931-04caf329c0c7.png",
    "#sha1_content" : "9fc2ae4d0d26d4b50c38ff2c5c235d33e8b56d1c",

    "user": {
        "id"  : "ef14099e-a6db-4325-9c67-51c0615985d5",
        "name": "sanka",
        "nick": "Cerodiers",
    },
    "id"            : "PbYJb57QqwrFp0",
    "title"         : "还没做完",
    "file_id"       : "0302deee-9cd5-4c1f-b931-04caf329c0c7",
    "filename"      : "0302deee-9cd5-4c1f-b931-04caf329c0c7",
    "extension"     : "png",
    "mime"          : "image/png",
    "size"          : 3564514,
    "width"         : 2560,
    "height"        : 1440,
    "duration"      : None,
    "type"          : "image",
    "date"          : "dt:2025-07-04 03:15:37",
    "date_updated"  : "dt:2025-07-04 03:15:53",
},

{
    "#url"     : "https://www.iwara.tv/image/sjqkK5EobXucju/ellen-joe-dancing",
    "#comment" : "WebM video with sound classified as 'image'",
    "#class"   : iwara.IwaraImageExtractor,
    "#results" : "https://i.iwara.tv/image/original/cf1686ac-9796-4213-bea3-71b6dcaac658/cf1686ac-9796-4213-bea3-71b6dcaac658.webm",

    "date"        : "dt:2025-07-07 17:06:47",
    "date_updated": "dt:2025-07-07 17:07:11",
    "duration"    : None,
    "extension"   : "webm",
    "file_id"     : "cf1686ac-9796-4213-bea3-71b6dcaac658",
    "filename"    : "cf1686ac-9796-4213-bea3-71b6dcaac658",
    "width"       : 1366,
    "height"      : 768,
    "id"          : "sjqkK5EobXucju",
    "mime"        : "video/webm",
    "size"        : 4747505,
    "subcategory" : "image",
    "title"       : "Ellen Joe Dancing To Body Shaming",
    "type"        : "image",
    "user": {
        "id"  : "f7625ea7-c1c8-416b-b929-a245892911a6",
        "name": "marzcade",
        "nick": "Marzcade",
    },
},

)
