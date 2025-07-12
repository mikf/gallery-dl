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
},

{
    "#url"          : "https://www.iwara.tv/profile/tyron82/playlists",
    "#class"        : iwara.IwaraUserPlaylistsExtractor,
    "#pattern"      : iwara.IwaraPlaylistExtractor.pattern,
    "#count"        : range(10, 20),
},

{
    "#url"          : "https://www.iwara.tv/playlist/01ea603a-4e70-4a36-bc28-dc717eebc2d7",
    "#category"     : ("", "iwara", "playlist"),
    "#class"        : iwara.IwaraPlaylistExtractor,
    "#pattern"      : r"https://\w+.iwara.tv/download\?filename=b7708020-f531-4eb4-bfd3-c62f3d17927e_Source.mp4&path=2024%2F05%2F12&.+",
    "#count"        : 1,

    "user_id"       : "c9a08dd5-3cb5-4d7c-b9bb-9eb4c55eda14",
    "username"      : "arisananades",
    "display_name"  : "Arisananades",
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
},

{
    "#url"          : "https://www.iwara.tv/search?query=genshin%20tentacle&type=video",
    "#category"     : ("", "iwara", "search"),
    "#class"        : iwara.IwaraSearchExtractor,
    "#count"        : 5,

    "user_id"       : "3ec40862-bcb6-4c2e-9f3b-6da3a00cc2d9",
    "username"      : "nizipaco-kyu",
    "display_name"  : "Nizipaco - Kyu",
    "extension"     : "mp4",
    "mime"          : "video/mp4",
    "width"         : None,
    "height"        : None,
    "type"          : "video",
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

    "user_id"       : "2b4391f3-c46f-43f9-b18f-8bdb8a9df74f",
    "username"      : "lenoria",
    "display_name"  : "lenoria",
    "extension"     : "mp4",
    "mime"          : "video/mp4",
    "width"         : None,
    "height"        : None,
    "type"          : "video",
    "search_tags"   : "aether,citlali",
    "search_type"   : "videos",
    "duration"      : range(90, 200),
},

{
    "#url"          : "https://www.iwara.tv/images?tags=genshin_impact%2Ccitlali",
    "#category"     : ("", "iwara", "tag"),
    "#class"        : iwara.IwaraTagExtractor,
    "#results"      : (
        "https://i.iwara.tv/image/original/c442c69f-30fb-4fd4-8f8f-338bbc77c07d/c442c69f-30fb-4fd4-8f8f-338bbc77c07d.jpg",
        "https://i.iwara.tv/image/original/7b53cc07-3640-4749-8c11-6da5f5a292a0/7b53cc07-3640-4749-8c11-6da5f5a292a0.jpg",
        "https://i.iwara.tv/image/original/373cc1cb-028e-44bd-aef3-3400de4f995b/373cc1cb-028e-44bd-aef3-3400de4f995b.jpg",
        "https://i.iwara.tv/image/original/0256b01b-8b4d-47f7-894d-2aceba6b8ab8/0256b01b-8b4d-47f7-894d-2aceba6b8ab8.jpg",
        "https://i.iwara.tv/image/original/8541dab6-9c67-419d-8af8-2e040ae487dc/8541dab6-9c67-419d-8af8-2e040ae487dc.png",
        "https://i.iwara.tv/image/original/8eba51de-c618-4853-964f-25f526b58398/8eba51de-c618-4853-964f-25f526b58398.webm",
    ),

    "duration"    : None,
    "extension"   : {"jpg", "png", "webm"},
    "mime"        : {"image/jpeg", "image/png", "video/webm"},
    "search_tags" : "genshin_impact,citlali",
    "search_type" : "images",
    "type"        : "image",
},

{
    "#url"          : "https://www.iwara.tv/video/6QvQvzZnELJ9vv/bluearchive-rio",
    "#category"     : ("", "iwara", "video"),
    "#class"        : iwara.IwaraVideoExtractor,
    "#pattern"      : r"https://\w+.iwara.tv/download\?filename=7ba6e734-b9df-4588-88fc-4eef2bbf5c56_Source.mp4&path=2025%2F07%2F05&expires=\d+&hash=[0-9a-f]{64}",
    "#count"        : 1,

    "user_id"       : "b3f86af1-874c-41f1-b62e-4e4b736ad3a4",
    "username"      : "croove",
    "display_name"  : "crooveNSFW",
    "id"            : "6QvQvzZnELJ9vv",
    "title"         : "[BlueArchive / ブルアカ] Rio",
    "file_id"       : "7ba6e734-b9df-4588-88fc-4eef2bbf5c56",
    "filename"      : "7ba6e734-b9df-4588-88fc-4eef2bbf5c56",
    "extension"     : "mp4",
    "mime"          : "video/mp4",
    "size"          : 86328642,
    "width"         : None,
    "height"        : None,
    "duration"      : 107,
    "type"          : "video",
    "date"          : "dt:2025-07-05 06:49:56",
    "date_updated"  : "dt:2025-07-05 06:50:14",
},

{
    "#url"          : "https://www.iwara.tv/image/5m3gLfcei6BQsL/sparkle",
    "#category"     : ("", "iwara", "image"),
    "#class"        : iwara.IwaraImageExtractor,
    "#pattern"      : r"https://i.iwara.tv/image/original/[\w-]{36}/[\w-]{36}\.png",
    "#count"        : 13,

    "user_id"       : "771d2b29-5935-43d7-85e1-30abbf47ccad",
    "username"      : "zcccz",
    "display_name"  : "zcccz",
    "id"            : "5m3gLfcei6BQsL",
    "title"         : "Sparkle",
    "extension"     : "png",
    "mime"          : "image/png",
    "type"          : "image",
    "date"          : "type:datetime",
    "date_updated"  : "type:datetime",
},

{
    "#url"          : "https://www.iwara.tv/image/PbYJb57QqwrFp0",
    "#category"     : ("", "iwara", "image"),
    "#class"        : iwara.IwaraImageExtractor,
    "#results"      : "https://i.iwara.tv/image/original/0302deee-9cd5-4c1f-b931-04caf329c0c7/0302deee-9cd5-4c1f-b931-04caf329c0c7.png",
    "#sha1_content" : "9fc2ae4d0d26d4b50c38ff2c5c235d33e8b56d1c",

    "user_id"       : "ef14099e-a6db-4325-9c67-51c0615985d5",
    "username"      : "sanka",
    "display_name"  : "Cerodiers",
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
    "display_name": "Marzcade",
    "duration"    : None,
    "extension"   : "webm",
    "file_id"     : "cf1686ac-9796-4213-bea3-71b6dcaac658",
    "filename"    : "cf1686ac-9796-4213-bea3-71b6dcaac658",
    "height"      : 768,
    "id"          : "sjqkK5EobXucju",
    "mime"        : "video/webm",
    "size"        : 4747505,
    "subcategory" : "image",
    "title"       : "Ellen Joe Dancing To Body Shaming",
    "type"        : "image",
    "user_id"     : "f7625ea7-c1c8-416b-b929-a245892911a6",
    "username"    : "marzcade",
    "width"       : 1366,
},

)
