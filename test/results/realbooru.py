# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import realbooru


__tests__ = (
{
    "#url"     : "https://realbooru.com/index.php?page=post&s=list&tags=wine",
    "#category": ("booru", "realbooru", "tag"),
    "#class"   : realbooru.RealbooruTagExtractor,
    "#count"   : ">= 64",
},

{
    "#url"     : "https://realbooru.com/index.php?page=pool&s=show&id=1",
    "#category": ("booru", "realbooru", "pool"),
    "#class"   : realbooru.RealbooruPoolExtractor,
    "#results" : (
        "https://video-cdn.realbooru.com//images/bf/d6/bfd682f338691e5254de796040fcba21.mp4",
        "https://video-cdn.realbooru.com//images/cb/7d/cb7d921673ba99f688031ac554777695.mp4",
        "https://video-cdn.realbooru.com//images/9e/14/9e140edc1cb2e4cc734ba5bdc4870955.mp4",
    ),
},

{
    "#url"     : "https://realbooru.com/index.php?page=favorites&s=view&id=274",
    "#category": ("booru", "realbooru", "favorite"),
    "#class"   : realbooru.RealbooruFavoriteExtractor,
    "#results" : "https://realbooru.com//images/20/3e/203eefb39f54de049e30ff788a022ac7.jpeg",
},

{
    "#url"     : "https://realbooru.com/index.php?page=post&s=view&id=862054",
    "#comment" : "regular post",
    "#category": ("booru", "realbooru", "post"),
    "#class"   : realbooru.RealbooruPostExtractor,
    "#results"     : "https://realbooru.com//images/8a/34/8a345820da989637c21ac013d522bf69.jpeg",
    "#sha1_content": "f6213e6f25c3cb9e3cfefa6d4b3a78e44b9dea5b",

    "created_at"    : "Jan, 18 2024",
    "date"          : "dt:2024-01-18 00:00:00",
    "file_url"      : "https://realbooru.com//images/8a/34/8a345820da989637c21ac013d522bf69.jpeg",
    "filename"      : "8a345820da989637c21ac013d522bf69",
    "id"            : "862054",
    "md5"           : "8a345820da989637c21ac013d522bf69",
    "rating"        : "e",
    "score"         : r"re:\d+",
    "source"        : "https://www.instagram.com/p/CwAO1UyJBnw",
    "tags"          : "1girl, asian, bikini, black_hair, breasts, cleavage, female, female_only, floral_print, instagram, japanese, kurita_emi, large_breasts, looking_at_viewer, navel, sauna, short_hair, side-tie_bikini, sitting, solo",
    "tags_copyright": "instagram",
    "tags_general"  : "1girl, asian, bikini, black_hair, breasts, cleavage, female, female_only, floral_print, large_breasts, looking_at_viewer, navel, sauna, short_hair, side-tie_bikini, sitting, solo",
    "tags_metadata" : "japanese",
    "tags_model"    : "kurita_emi",
},

{
    "#url"     : "https://realbooru.com/index.php?page=post&s=view&id=568145",
    "#comment" : "older post",
    "#category": ("booru", "realbooru", "post"),
    "#class"   : realbooru.RealbooruPostExtractor,
    "#sha1_content": "4a7424810f5f846c161b5d3b7c8b0a85a03368c8",
},

{
    "#url"     : "https://realbooru.com/index.php?page=post&s=view&id=825911",
    "#comment" : "animated GIF",
    "#category": ("booru", "realbooru", "post"),
    "#class"   : realbooru.RealbooruPostExtractor,
    "#results" : "https://realbooru.com//images/a3/9b/a39bfe5ea07f132db486e118b598c66c.gif",

    "created_at"   : "Feb, 19 2023",
    "date"         : "dt:2023-02-19 00:00:00",
    "extension"    : "gif",
    "file_url"     : "https://realbooru.com//images/a3/9b/a39bfe5ea07f132db486e118b598c66c.gif",
    "filename"     : "a39bfe5ea07f132db486e118b598c66c",
    "id"           : "825911",
    "md5"          : "a39bfe5ea07f132db486e118b598c66c",
    "rating"       : "e",
    "score"        : r"re:\d+",
    "source"       : "",
    "title"        : "",
    "uploader"     : "freakyguro",
    "tags"         : "1girl, amateur, animated, animated_gif, asian, ass, ass_shake, biting_lip, breasts, brown_hair, butt, cute, fringe, girlfriend, japanese, japanese_(nationality), kitchen, looking_at_viewer, looking_back, medium_breasts, obokozu, panties, petite, seductive_eyes, seductive_smile, solo, underwear",
    "tags_general" : "1girl, asian, ass, ass_shake, biting_lip, breasts, brown_hair, butt, cute, fringe, girlfriend, japanese_(nationality), kitchen, looking_at_viewer, looking_back, medium_breasts, panties, petite, seductive_eyes, seductive_smile, solo, underwear",
    "tags_metadata": "amateur, animated, animated_gif, japanese",
    "tags_model"   : "obokozu",
},

{
    "#url"     : "https://realbooru.com/index.php?page=post&s=view&id=751237",
    "#comment" : "video",
    "#category": ("booru", "realbooru", "post"),
    "#class"   : realbooru.RealbooruPostExtractor,
    "#results" : "https://video-cdn.realbooru.com//images/3c/34/3c343385126c90a7fdbccc58d342a511.mp4",

    "created_at"    : "Dec, 07 2020",
    "date"          : "dt:2020-12-07 00:00:00",
    "extension"     : "mp4",
    "file_url"      : "https://video-cdn.realbooru.com//images/3c/34/3c343385126c90a7fdbccc58d342a511.mp4",
    "filename"      : "3c343385126c90a7fdbccc58d342a511",
    "id"            : "751237",
    "md5"           : "3c343385126c90a7fdbccc58d342a511",
    "rating"        : "e",
    "score"         : r"re:\d+",
    "source"        : "",
    "title"         : "",
    "uploader"      : "Rock 7800",
    "tags"          : "1girl, animated, anri_okita, asian, breasts, brown_hair, brunette, dress, dress_pull, female, female_only, female_solo, huge_breasts, human_only, japanese, lipstick, makeup, model, mostly_clothed, nadine-j, nipples, no_bra, no_sound, topless, undressing, webm",
    "tags_copyright": "nadine-j",
    "tags_general"  : "1girl, asian, breasts, brown_hair, brunette, dress, dress_pull, female, female_only, female_solo, huge_breasts, human_only, lipstick, makeup, mostly_clothed, nipples, no_bra, topless, undressing",
    "tags_metadata" : "animated, japanese, model, no_sound, webm",
    "tags_model"    : "anri_okita",
},

)
