# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import yiffverse


__tests__ = (
{
    "#url"    : "https://yiffverse.com/post/574342",
    "#comment": "image",
    "#class"  : yiffverse.YiffversePostExtractor,
    "#options"     : {"tags": True},
    "#urls"        : "https://yiffverse.com/posts/574/574342/574342.pic.jpg",
    "#sha1_content": "0f169fddbd320eae904508f83a722bb3633ad507",

    "created"  : "2024-12-06T13:55:24.483002Z",
    "date"     : "dt:2024-12-06 13:55:24",
    "extension": "jpg",
    "file_url" : "https://yiffverse.com/posts/574/574342/574342.pic.jpg",
    "filename" : "574342",
    "format"   : "pic",
    "format_id": "10",
    "height"   : 862,
    "id"       : 574342,
    "likes"    : range(5, 100),
    "posted"   : "2024-12-06T13:55:55.299953Z",
    "status"   : 2,
    "type"     : 0,
    "tags"        : list,
    "tags_general": list,
    "tags_artist" : ["imanika"],
    "uploaderId"  : 2,
    "width"       : 950,
    "data"        : {
        "sources": [
            "https://www.furaffinity.net/view/59071676/",
            "https://www.furaffinity.net/user/imanika/",
            "https://d.furaffinity.net/art/imanika/1733430246/1733430246.imanika_dream_girl_ych_slot1_web.jpg",
        ],
    },
    "uploader"    : {
        "created"      : "2021-07-04T15:01:03.110916Z",
        "data"         : None,
        "displayName"  : "agent.e621-uploader",
        "emailVerified": False,
        "id"           : 2,
        "role"         : 3,
        "userName"     : "agent.e621-uploader",
    },
},

{
    "#url"    : "https://yiffverse.com/post/575680",
    "#comment": "video",
    "#class"  : yiffverse.YiffversePostExtractor,
    "#urls"        : "https://yiffverse.com/posts/575/575680/575680.mov.mp4",
    "#sha1_content": "8952fc794e58c531b4e3b01cfe9e14b1c59ad9ef",
},

{
    "#url"  : "https://yiffverse.com/tag/tree",
    "#class": yiffverse.YiffverseTagExtractor,
    "#pattern": r"https://yiffverse\.com/posts/\d+/\d+/\d+\.(pic\.jpg|mov\d*\.mp4)",
    "#range"  : "1-10",
    "#count"  : 10,
},

{
    "#url"  : "https://yiffverse.com/playlist/6842",
    "#class": yiffverse.YiffversePlaylistExtractor,
    "#pattern": r"https://(yiffverse\.com|furry34com\.b-cdn\.net)/posts/\d+/\d+/\d+\.mov(720)?\.mp4",
    "#count"  : 25,
},

)
