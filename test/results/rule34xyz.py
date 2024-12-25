# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import rule34xyz


__tests__ = (
{
    "#url"  : "https://rule34.xyz/sfw",
    "#class": rule34xyz.Rule34xyzTagExtractor,
    "#pattern": r"https://rule34(\.xyz|xyz\.b-cdn\.net)/posts/\d+/\d+/\d+\.(pic|mov\d*)\.(jpg|mp4)",
    "#range"  : "1-150",
    "#count"  : 150,

    "search_tags": "sfw",
},

{
    "#url"  : "https://rule34.xyz/playlists/view/119",
    "#class": rule34xyz.Rule34xyzPlaylistExtractor,
    "#pattern": r"https://rule34(\.xyz|xyz\.b-cdn\.net)/posts/\d+/\d+/\d+\.(pic|mov\d*)\.(jpg|mp4)",
    "#count"  : 64,

    "playlist_id": "119",
},

{
    "#url"    : "https://rule34.xyz/post/3613851",
    "#comment": "image",
    "#class"  : rule34xyz.Rule34xyzPostExtractor,
    "#options"     : {"tags": True},
    "#urls"        : "https://rule34xyz.b-cdn.net/posts/3613/3613851/3613851.pic.jpg",
    "#sha1_content": "4d7146db258fd5b1645a1a5fc01550d102f495e1",

    "attributes": 1,
    "comments"  : 0,
    "created"   : "2023-03-29T06:00:59.136819",
    "date"      : "dt:2023-03-29 06:00:59",
    "duration"  : None,
    "error"     : None,
    "extension" : "jpg",
    "file_url"  : "https://rule34xyz.b-cdn.net/posts/3613/3613851/3613851.pic.jpg",
    "filename"  : "3613851.pic",
    "format"    : "pic",
    "format_id" : "2",
    "id"        : 3613851,
    "likes"     : range(3, 100),
    "posted"    : "2023-03-29T06:01:07.900161",
    "type"      : 0,
    "uploaderId": 9741,
    "views"     : range(200, 2000),
    "status"    : 2,
    "files"     : dict,
    "sources": [
        "https://twitter.com/DesireDelta13/status/1636502494292373505?t=OrmlnC85cELyY5BPmBy9Hw&s=19",
    ],
    "tags": [
        "doki doki literature club",
        "doki doki takeover",
        "friday night funkin",
        "friday night funkin mod",
        "yuri (doki doki literature club)",
        "desiredelta",
        "1girls",
        "big breasts",
        "clothed",
        "clothed female",
        "female",
        "female focus",
        "female only",
        "holding microphone",
        "holding object",
        "long hair",
        "long purple hair",
        "looking at viewer",
        "microphone",
        "open hand",
        "open mouth",
        "purple background",
        "purple hair",
        "solo",
        "solo female",
        "solo focus",
        "sweater",
        "white outline",
        "jpeg",
        "safe for work",
        "sfw",
    ],
    "tags_artist": [
        "desiredelta",
    ],
    "tags_character": [
        "yuri (doki doki literature club)",
    ],
    "tags_copyright": [
        "doki doki literature club",
        "friday night funkin",
        "friday night funkin mod",
    ],
    "tags_general": list,
    "uploader": {
        "avatarUrl"      : None,
        "bookmarks"      : 0,
        "certified"      : True,
        "created"        : "2021-04-03T08:29:51.373823",
        "email"          : "agent.rulexxx-uploader@z.com",
        "id"             : 9741,
        "isSystemAccount": True,
        "name"           : "agent.rulexxx-uploader",
        "role"           : 2,
        "uploadedPosts"  : range(100000, 999999),
        "webId"          : None,
    },
},

{
    "#url"    : "https://rule34.xyz/post/3571567",
    "#comment": "video",
    "#class"  : rule34xyz.Rule34xyzPostExtractor,
    "#urls"        : "https://rule34xyz.b-cdn.net/posts/3571/3571567/3571567.mov720.mp4",
    "#sha1_content": "c0a5e7e887774f91527f00e6142c435a3c482c1f",

    "format"    : "mov720",
    "format_id" : "40",
},

{
    "#url"    : "https://rule34.xyz/post/3571567",
    "#comment": "'format' option",
    "#class"  : rule34xyz.Rule34xyzPostExtractor,
    "#options": {"format": "10,33"},
    "#urls"   : "https://rule34xyz.b-cdn.net/posts/3571/3571567/3571567.pic256avif.avif",

    "format"    : "pic256avif",
    "format_id" : "33",
},

)
