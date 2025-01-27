# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import philomena


__tests__ = (
{
    "#url"     : "https://derpibooru.org/images/1",
    "#category": ("philomena", "derpibooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
    "#count"       : 1,
    "#sha1_content": "88449eeb0c4fa5d3583d0b794f6bc1d70bf7f889",

    "animated"        : False,
    "aspect_ratio"    : 1.0,
    "comment_count"   : int,
    "created_at"      : "2012-01-02T03:12:33Z",
    "date"            : "dt:2012-01-02 03:12:33",
    "deletion_reason" : None,
    "description"     : "",
    "downvotes"       : int,
    "duplicate_of"    : None,
    "duration"        : 0.04,
    "extension"       : "png",
    "faves"           : int,
    "first_seen_at"   : "2012-01-02T03:12:33Z",
    "format"          : "png",
    "height"          : 900,
    "hidden_from_users": False,
    "id"              : 1,
    "mime_type"       : "image/png",
    "name"            : "1__safe_fluttershy_solo_cloud_happy_flying_upvotes+galore_artist-colon-speccysy_get_sunshine",
    "orig_sha512_hash": None,
    "processed"       : True,
    "representations" : dict,
    "score"           : int,
    "sha512_hash"     : "f16c98e2848c2f1bfff3985e8f1a54375cc49f78125391aeb80534ce011ead14e3e452a5c4bc98a66f56bdfcd07ef7800663b994f3f343c572da5ecc22a9660f",
    "size"            : 860914,
    "source_url"      : "https://web.archive.org/web/20110702164313/http://speccysy.deviantart.com:80/art/Afternoon-Flight-215193985",
    "spoilered"       : False,
    "tag_count"       : int,
    "tag_ids"         : list,
    "tags"            : list,
    "thumbnails_generated": True,
    "updated_at"      : r"re:\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ",
    "uploader"        : "Clover the Clever",
    "uploader_id"     : 211188,
    "upvotes"         : int,
    "view_url"        : str,
    "width"           : 900,
    "wilson_score"    : float,
},

{
    "#url"     : "https://derpibooru.org/images/3334658",
    "#comment" : "svg (#5643)",
    "#category": ("philomena", "derpibooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
    "#urls"        : "https://derpicdn.net/img/view/2024/4/1/3334658__safe_alternate+version_artist-colon-jp_derpibooru+exclusive_twilight+sparkle_alicorn_pony_amending+fences_g4_my+little+pony-colon-+friendship+is+magic_.svg",
    "#sha1_content": "eec5adf02e2a4fe83b9211c0444d57dc03e21f50",

    "extension": "svg",
    "format"   : "svg",
},

{
    "#url"     : "https://derpibooru.org/1",
    "#category": ("philomena", "derpibooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
},

{
    "#url"     : "https://www.derpibooru.org/1",
    "#category": ("philomena", "derpibooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
},

{
    "#url"     : "https://www.derpibooru.org/images/1",
    "#category": ("philomena", "derpibooru", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
},

{
    "#url"     : "https://derpibooru.org/search?q=cute",
    "#category": ("philomena", "derpibooru", "search"),
    "#class"   : philomena.PhilomenaSearchExtractor,
    "#range"   : "40-60",
    "#count"   : 21,
},

{
    "#url"     : "https://derpibooru.org/tags/cute",
    "#category": ("philomena", "derpibooru", "search"),
    "#class"   : philomena.PhilomenaSearchExtractor,
    "#range"   : "40-60",
    "#count"   : 21,
},

{
    "#url"     : "https://derpibooru.org/tags/artist-colon--dash-_-fwslash--fwslash-%255Bkorroki%255D_aternak",
    "#category": ("philomena", "derpibooru", "search"),
    "#class"   : philomena.PhilomenaSearchExtractor,
    "#count"   : ">= 2",
},

{
    "#url"     : "https://derpibooru.org/galleries/1",
    "#category": ("philomena", "derpibooru", "gallery"),
    "#class"   : philomena.PhilomenaGalleryExtractor,
    "#pattern" : r"https://derpicdn\.net/img/view/\d+/\d+/\d+/\d+[^/]+$",

    "gallery": {
        "description"    : "Indexes start at 1 :P",
        "id"             : 1,
        "spoiler_warning": "",
        "thumbnail_id"   : 1,
        "title"          : "The Very First Gallery",
        "user"           : "DeliciousBlackInk",
        "user_id"        : 365446,
    },
},

)
