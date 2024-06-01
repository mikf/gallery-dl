# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gelbooru_v02


__tests__ = (
{
    "#url"     : "https://realbooru.com/index.php?page=post&s=list&tags=wine",
    "#category": ("gelbooru_v02", "realbooru", "tag"),
    "#class"   : gelbooru_v02.GelbooruV02TagExtractor,
    "#count"   : ">= 64",
},

{
    "#url"     : "https://realbooru.com/index.php?page=pool&s=show&id=1",
    "#category": ("gelbooru_v02", "realbooru", "pool"),
    "#class"   : gelbooru_v02.GelbooruV02PoolExtractor,
    "#urls"    : (
        "https://realbooru.com//images/bf/d6/bfd682f338691e5254de796040fcba21.webm",
        "https://realbooru.com//images/cb/7d/cb7d921673ba99f688031ac554777695.webm",
        "https://realbooru.com//images/9e/14/9e140edc1cb2e4cc734ba5bdc4870955.webm",
    ),
},

{
    "#url"     : "https://realbooru.com/index.php?page=favorites&s=view&id=274",
    "#category": ("gelbooru_v02", "realbooru", "favorite"),
    "#class"   : gelbooru_v02.GelbooruV02FavoriteExtractor,
    "#urls"    : (
        "https://realbooru.com//images/20/3e/0c2c4d8c978355c053602dc963eb13136c1614c1.jpeg",
    ),
},

{
    "#url"     : "https://realbooru.com/index.php?page=post&s=view&id=862054",
    "#comment" : "regular post",
    "#category": ("gelbooru_v02", "realbooru", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#options"     : {"tags": True},
    "#urls"        : "https://realbooru.com//images/8a/34/8a345820da989637c21ac013d522bf69.jpeg",
    "#sha1_content": "f6213e6f25c3cb9e3cfefa6d4b3a78e44b9dea5b",

    "change"        : "1705562002",
    "created_at"    : "Thu Jan 18 01:12:50 -0600 2024",
    "creator_id"    : "32011",
    "date"          : "dt:2024-01-18 07:12:50",
    "file_url"      : "https://realbooru.com//images/8a/34/8a345820da989637c21ac013d522bf69.jpeg",
    "filename"      : "8a345820da989637c21ac013d522bf69",
    "has_children"  : "false",
    "has_comments"  : "false",
    "has_notes"     : "false",
    "height"        : "1800",
    "id"            : "862054",
    "md5"           : "8a345820da989637c21ac013d522bf69",
    "parent_id"     : "",
    "preview_height": "150",
    "preview_url"   : "https://realbooru.com/thumbnails/8a/34/thumbnail_8a345820da989637c21ac013d522bf69.jpg",
    "preview_width" : "120",
    "rating"        : "e",
    "sample_height" : "1063",
    "sample_url"    : "https://realbooru.com/samples/8a/34/sample_8a345820da989637c21ac013d522bf69.jpg",
    "sample_width"  : "850",
    "score"         : "",
    "source"        : "https://www.instagram.com/p/CwAO1UyJBnw",
    "status"        : "active",
    "tags"          : " 1girl asian bikini black_hair breasts cleavage female female_only floral_print instagram japanese kurita_emi large_breasts looking_at_viewer navel sauna short_hair side-tie_bikini sitting solo ",
    "tags_copyright": "instagram",
    "tags_general"  : "1girl asian bikini black_hair breasts cleavage female female_only floral_print japanese large_breasts looking_at_viewer navel sauna short_hair side-tie_bikini sitting solo",
    "tags_model"    : "kurita_emi",
    "width"         : "1440",
},

{
    "#url"     : "https://realbooru.com/index.php?page=post&s=view&id=568145",
    "#comment" : "older post",
    "#category": ("gelbooru_v02", "realbooru", "post"),
    "#class"   : gelbooru_v02.GelbooruV02PostExtractor,
    "#sha1_content": "4a7424810f5f846c161b5d3b7c8b0a85a03368c8",
},

)
