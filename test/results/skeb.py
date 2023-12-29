# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import skeb


__tests__ = (
{
    "#url"     : "https://skeb.jp/@kanade_cocotte/works/38",
    "#category": ("", "skeb", "post"),
    "#class"   : skeb.SkebPostExtractor,
    "#count"   : 2,

    "anonymous"       : False,
    "body"            : r"re:はじめまして。私はYouTubeにてVTuberとして活動をしている湊ラ",
    "client"          : {
        "avatar_url" : r"re:https://pbs.twimg.com/profile_images/\d+/\w+\.jpg",
        "header_url" : r"re:https://pbs.twimg.com/profile_banners/1375007870291300358/\d+/1500x500",
        "id"         : 1196514,
        "name"       : str,
        "screen_name": "minato_ragi",
    },
    "content_category": "preview",
    "creator"         : {
        "avatar_url" : "https://pbs.twimg.com/profile_images/1225470417063645184/P8_SiB0V.jpg",
        "header_url" : "https://pbs.twimg.com/profile_banners/71243217/1647958329/1500x500",
        "id"         : 159273,
        "name"       : "イチノセ奏",
        "screen_name": "kanade_cocotte",
    },
    "file_id"         : int,
    "file_url"        : str,
    "genre"           : "art",
    "nsfw"            : False,
    "original"        : {
        "byte_size" : int,
        "duration"  : None,
        "extension" : r"re:psd|png",
        "frame_rate": None,
        "height"    : 3727,
        "is_movie"  : False,
        "width"     : 2810,
    },
    "post_num"        : "38",
    "post_url"        : "https://skeb.jp/@kanade_cocotte/works/38",
    "source_body"     : None,
    "source_thanks"   : None,
    "tags"            : list,
    "thanks"          : None,
    "translated_body" : False,
    "translated_thanks": None,
},

{
    "#url"     : "https://skeb.jp/@kanade_cocotte",
    "#category": ("", "skeb", "user"),
    "#class"   : skeb.SkebUserExtractor,
    "#pattern" : r"https://si\.imgix\.net/\w+/uploads/origins/[\w-]+",
    "#range"   : "1-5",
},

{
    "#url"     : "https://skeb.jp/search?q=bunny%20tree&t=works",
    "#category": ("", "skeb", "search"),
    "#class"   : skeb.SkebSearchExtractor,
    "#count"   : ">= 18",

    "search_tags": "bunny tree",
},

{
    "#url"     : "https://skeb.jp/@user/following_creators",
    "#category": ("", "skeb", "following"),
    "#class"   : skeb.SkebFollowingExtractor,
},

)
