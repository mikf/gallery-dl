# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import rule34vault


__tests__ = (
{
    "#url"  : "https://rule34vault.com/sfw",
    "#class": rule34vault.Rule34vaultTagExtractor,
    "#pattern": r"https://r34xyz\.b-cdn\.net/posts/\d+/\d+/\d+\.(jpg|mp4)",
    "#range"  : "1-10",
    "#count"  : 10,
},

{
    "#url"  : "https://rule34vault.com/playlists/view/20164",
    "#class": rule34vault.Rule34vaultPlaylistExtractor,
    "#pattern": r"https://r34xyz\.b-cdn\.net/posts/\d+/\d+/\d+\.(jpg|mp4)",
    "#count"  : range(55, 75),
},

{
    "#url"    : "https://rule34vault.com/post/280517",
    "#comment": "image",
    "#class"  : rule34vault.Rule34vaultPostExtractor,
    "#options": {"tags": True},
    "#pattern"     : "https://r34xyz.b-cdn.net/posts/280/280517/280517.jpg",
    "#sha1_content": "1e19d601b4a79c06e6f885a83a5003e7e2a17057",

    "created"   : "2023-09-01T11:57:57.317331Z",
    "date"      : "dt:2023-09-01 11:57:57",
    "extension" : "jpg",
    "file_url"  : "https://r34xyz.b-cdn.net/posts/280/280517/280517.jpg",
    "filename"  : "280517",
    "height"    : 1152,
    "id"        : 280517,
    "likes"     : range(3, 100),
    "posted"    : "2023-09-01T12:01:41.008547Z",
    "status"    : 2,
    "type"      : 0,
    "uploaderId": 20678,
    "views"     : range(90, 999),
    "width"     : 768,
    "data": {
        "sources": [
            "https://trynectar.ai/view/87c98fc8-e4f3-447c-a0d3-024b1890580a",
        ],
    },
    "tags": [
        "ai generated",
        "demon slayer",
        "kamado nezuko",
        "school uniform",
        "sfw",
    ],
    "tags_character": [
        "kamado nezuko",
    ],
    "tags_copyright": [
        "demon slayer",
    ],
    "tags_general": [
        "ai generated",
        "school uniform",
        "sfw",
    ],
    "uploader": {
        "created"      : "2023-07-24T04:33:36.734495Z",
        "data"         : None,
        "displayName"  : "quick1e",
        "emailVerified": False,
        "id"           : 20678,
        "role"         : 1,
        "userName"     : "quick1e",
    },
},

{
    "#url"    : "https://rule34vault.com/post/382937",
    "#comment": "video",
    "#class"  : rule34vault.Rule34vaultPostExtractor,
    "#urls"        : "https://r34xyz.b-cdn.net/posts/382/382937/382937.mp4",
    "#sha1_content": "b962e3e2304139767c3792508353e6e83a85a2af",
},

)
