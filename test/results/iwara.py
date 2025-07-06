# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import iwara


__tests__ = (
{
    "#url"          : "https://www.iwara.tv/profile/user2426993",
    "#category"     : ("", "iwara", "profile"),
    "#class"        : iwara.IwaraProfileExtractor,
    "#count"        : 6,
    "#sha1_content" : "92730533a0db39a440fdfb9b7250c806207a3faf",
    "#sha1_metadata": "0ebd9be904e56215bab9f3b62ea14e3b90bfa28f",

    "user_id"       : "67059990-acdb-4d4f-9a88-abe81136bff1",
    "username"      : "user2426993",
    "display_name"  : "桜飘の季節",
},

{
    "#url"          : "https://www.iwara.tv/playlist/01ea603a-4e70-4a36-bc28-dc717eebc2d7",
    "#category"     : ("", "iwara", "playlist"),
    "#class"        : iwara.IwaraPlaylistExtractor,
    "#count"        : 1,
    "#sha1_content" : "6096ef4b124795281bcf95e07157c2f294199dec",
    "#sha1_metadata": "bd2da5b066e86a5809b41c76596ff17effed32ba",

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
    "datetime"      : "Sun, May 12, 2024 11:49:53",
    "type"          : "video",
},

{
    "#url"          : "https://www.iwara.tv/search?query=genshin%20tentacle&type=video",
    "#category"     : ("", "iwara", "search"),
    "#class"        : iwara.IwaraSearchExtractor,
    "#count"        : 5,
    "#sha1_content" : "880e2b5191e555594f790dafa58b5a055f91d4fb",
    "#sha1_metadata": "0cc633020856afe0f485ac7d535799375d86f502",

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
    "#sha1_content" : "38aeed4ab6d2a8e91edfd10a1efafaad22868005",
    "#sha1_metadata": "1918d47f23d6b87790e0e27021717f5c7270c3fc",

    "duration"      : None,
    "type"          : "image",
},

{
    "#url"          : "https://www.iwara.tv/videos?tags=aether%2Ccitlali",
    "#category"     : ("", "iwara", "tag"),
    "#class"        : iwara.IwaraTagExtractor,
    "#count"        : 3,
    "#sha1_content" : "71b4b99ccccbe93e0d2be8c828f10d30907dacd0",
    "#sha1_metadata": "e582e14ac242c7753d813b44f24d7387c41d2b16",

    "user_id"       : "2b4391f3-c46f-43f9-b18f-8bdb8a9df74f",
    "username"      : "lenoria",
    "display_name"  : "lenoria",
    "extension"     : "mp4",
    "mime"          : "video/mp4",
    "width"         : None,
    "height"        : None,
    "type"          : "video",
},

{
    "#url"          : "https://www.iwara.tv/images?tags=genshin_impact%2Ccitlali",
    "#category"     : ("", "iwara", "tag"),
    "#class"        : iwara.IwaraTagExtractor,
    "#count"        : 6,
    "#sha1_content" : "b550513726dbba9e902c309ffddcb22244be2524",
    "#sha1_metadata": "7d765b5531dac9340dd9b0218a8cc8b3b730696f",

    "duration"      : None,
    "type"          : "image",
},

{
    "#url"          : "https://www.iwara.tv/video/6QvQvzZnELJ9vv/bluearchive-rio",
    "#category"     : ("", "iwara", "video"),
    "#class"        : iwara.IwaraVideoExtractor,
    "#count"        : 1,
    "#sha1_content" : "2c2004daae067459466cdb5bbd8fe260c079f29a",
    "#sha1_metadata": "1d62d855149b1fd18b0d13da8500166fd3986b29",

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
    "datetime"      : "Sat, Jul 5, 2025 06:49:56",
    "type"          : "video",
},

{
    "#url"          : "https://www.iwara.tv/image/5m3gLfcei6BQsL/sparkle",
    "#category"     : ("", "iwara", "image"),
    "#class"        : iwara.IwaraImageExtractor,
    "#count"        : 13,
    "#sha1_content" : "989756ef85679e34e2bdc413ad9b09c90aab82c6",
    "#sha1_metadata": "d9dbd835d5a0b89bd56e731a49d0ad5917b5ef8d",

    "user_id"       : "771d2b29-5935-43d7-85e1-30abbf47ccad",
    "username"      : "zcccz",
    "display_name"  : "zcccz",
    "id"            : "5m3gLfcei6BQsL",
    "title"         : "Sparkle",
    "extension"     : "png",
    "mime"          : "image/png",
    "type"          : "image",
},

{
    "#url"          : "https://www.iwara.tv/image/PbYJb57QqwrFp0",
    "#category"     : ("", "iwara", "image"),
    "#class"        : iwara.IwaraImageExtractor,
    "#count"        : 1,
    "#sha1_content" : "9fc2ae4d0d26d4b50c38ff2c5c235d33e8b56d1c",
    "#sha1_metadata": "5e9c748d08686b7a3a1a5bd50db716f8898c11b6",

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
    "datetime"      : "Fri, Jul 4, 2025 03:15:37",
    "type"          : "image",
},

)
