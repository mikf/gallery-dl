# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import twibooru


__tests__ = (
{
    "#url"     : "https://twibooru.org/1",
    "#category": ("philomena", "twibooru", "post"),
    "#class"   : twibooru.TwibooruPostExtractor,
    "#pattern"     : "https://cdn.twibooru.org/img/2020/7/8/1/full.png",
    "#sha1_content": "aac4d1dba611883ac701aaa8f0b2b322590517ae",

    "animated"        : False,
    "aspect_ratio"    : 1.0,
    "comment_count"   : int,
    "created_at"      : "2020-07-08T22:26:55.743Z",
    "date"            : "dt:2020-07-08 22:26:55",
    "description"     : "Why have I done this?",
    "downvotes"       : 0,
    "duration"        : 0.0,
    "faves"           : int,
    "first_seen_at"   : "2020-07-08T22:26:55.743Z",
    "format"          : "png",
    "height"          : 576,
    "hidden_from_users": False,
    "id"              : 1,
    "intensities"     : dict,
    "locations"       : [],
    "media_type"      : "image",
    "mime_type"       : "image/png",
    "name"            : "1676547__safe_artist-colon-scraggleman_oc_oc-colon-floor+bored_oc+only_bags+under+eyes_bust_earth+pony_female_goggles_helmet_mare_meme_neet_neet+home+g.png",
    "orig_sha512_hash": r"re:8b4c00d2[0-9a-f]{120}",
    "processed"       : True,
    "representations" : dict,
    "score"           : int,
    "sha512_hash"     : "8b4c00d2eff52d51ad9647e14738944ab306fd1d8e1bf634fbb181b32f44070aa588938e26c4eb072b1eb61489aaf3062fb644a76c79f936b97723a2c3e0e5d3",
    "size"            : 70910,
    "source_url"      : "",
    "tag_ids"         : list,
    "tags"            : list,
    "thumbnails_generated": True,
    "updated_at"      : str,
    "upvotes"         : int,
    "view_url"        : "https://cdn.twibooru.org/img/2020/7/8/1/full.png",
    "width"           : 576,
    "wilson_score"    : float,
},

{
    "#url"     : "https://twibooru.org/search?q=cute",
    "#category": ("philomena", "twibooru", "search"),
    "#class"   : twibooru.TwibooruSearchExtractor,
    "#range"   : "40-60",
    "#count"   : 21,
},

{
    "#url"     : "https://twibooru.org/tags/cute",
    "#category": ("philomena", "twibooru", "search"),
    "#class"   : twibooru.TwibooruSearchExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://twibooru.org/galleries/1",
    "#category": ("philomena", "twibooru", "gallery"),
    "#class"   : twibooru.TwibooruGalleryExtractor,
    "#range"   : "1-20",

    "gallery": {
        "description"    : "Best nation pone and russian related pics.",
        "id"             : 1,
        "spoiler_warning": "Russia",
        "thumbnail_id"   : 694923,
        "title"          : "Marussiaverse",
    },
},

)
