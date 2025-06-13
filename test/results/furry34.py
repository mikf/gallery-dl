# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import furry34


__tests__ = (
{
    "#url"    : "https://furry34.com/post/541949",
    "#comment": "image",
    "#class"  : furry34.Furry34PostExtractor,
    "#options"     : {"tags": True},
    "#results"     : "https://furry34com.b-cdn.net/posts/541/541949/541949.pic.jpg",
    "#sha1_content": "4880da04f7fb41b1760aad4c8297c9917aeeec53",

    "created"   : "2024-09-20T19:49:47.443232Z",
    "date"      : "dt:2024-09-20 19:49:47",
    "extension" : "jpg",
    "file_url"  : "https://furry34com.b-cdn.net/posts/541/541949/541949.pic.jpg",
    "filename"  : "541949",
    "format"    : "pic",
    "format_id" : "10",
    "id"        : 541949,
    "likes"     : 8,
    "posted"    : "2024-09-20T19:50:05.772166Z",
    "status"    : 2,
    "type"      : 0,
    "uploaderId": 2,
    "width"     : 1300,
    "height"    : 1920,

    "data": {
        "sources": [
            "https://x.com/EchoeDragon/status/1834316160252477741",
            "https://pbs.twimg.com/media/GXTMHFkWYAA8wDj?format=jpg&name=orig",
        ],
    },
    "tags": [
        "echodragon",
        "scp-1471",
        "scp-1471-a",
        "scp-1471-a (da.nilkaz)",
        "scp foundation",
        "canid",
        "canine",
        "malo",
        "mammal",
        "anthro",
        "big breasts",
        "black hair",
        "breasts",
        "cleavage",
        "clothed",
        "clothing",
        "female",
        "hair",
        "orange jumpsuit",
        "prison uniform",
        "solo",
        "tail",
        "thick thighs",
        "white eyes",
        "3d (artwork)",
        "digital media (artwork)",
        "hi res",
    ],
    "tags_artist": [
        "echodragon",
    ],
    "tags_character": [
        "scp-1471",
        "scp-1471-a",
        "scp-1471-a (da.nilkaz)",
    ],
    "tags_copyright": [
        "scp foundation",
    ],
    "tags_general": [
        "canid",
        "canine",
        "malo",
        "mammal",
        "anthro",
        "big breasts",
        "black hair",
        "breasts",
        "cleavage",
        "clothed",
        "clothing",
        "female",
        "hair",
        "orange jumpsuit",
        "prison uniform",
        "solo",
        "tail",
        "thick thighs",
        "white eyes",
        "3d (artwork)",
        "digital media (artwork)",
        "hi res",
    ],
    "uploader": {
        "attributes" : [
            80,
        ],
        "avatarModifyDate": None,
        "created"    : "2021-07-04T15:01:03.110916Z",
        "data"       : None,
        "displayName": "agent.e621-uploader",
        "emailVerified": False,
        "id"         : 2,
        "role"       : 3,
        "userName"   : "agent.e621-uploader",
    },
},

{
    "#url"    : "https://furry34.com/post/605309",
    "#comment": "video",
    "#class"  : furry34.Furry34PostExtractor,
    "#results"     : "https://furry34.com/posts/605/605309/605309.mov.mp4",
    "#sha1_content": "914d00e2a6cfee73547bae266ec4b7aaee5aadf2",

    "type": 1,
},

{
    "#url"  : "https://furry34.com/tree",
    "#class": furry34.Furry34TagExtractor,
    "#pattern": r"https://(furry34\.com|furry34com\.b-cdn\.net)/posts/\d+/\d+/\d+\.(pic\.jpg|mov\d*\.mp4)",
    "#range"  : "1-10",
    "#count"  : 10,
},

{
    "#url"  : "https://furry34.com/dariana_%2528quetzaly%2529%257Canimated?type=video",
    "#class": furry34.Furry34TagExtractor,
    "#pattern": r"https://(furry34\.com|furry34com\.b-cdn\.net)/posts/\d+/\d+/\d+\.(pic\.jpg|mov\d*\.mp4)",
    "#count"  : range(8, 20),

    "type": 1,
},

{
    "#url"  : "https://furry34.com/playlists/view/8966",
    "#class": furry34.Furry34PlaylistExtractor,
    "#pattern": r"https://(furry34\.com|furry34com\.b-cdn\.net)/posts/\d+/\d+/\d+\.mov(720)?\.mp4",
    "#count"  : range(50, 75),
},

)
