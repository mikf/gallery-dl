# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nudebird

__tests__ = (

{
    "#url"     : "https://nudebird.biz/category/cosplay/",
    "#class"   : nudebird.NudebirdCategoryExtractor,
    "#pattern" : nudebird.NudebirdPostExtractor.pattern,
    "#count"   : ">=938",

    "category_slug": "cosplay"
},

{
    "#url"     : "https://nudebird.biz/tag/dead-or-alive/",
    "#class"   : nudebird.NudebirdTagExtractor,
    "#pattern" : nudebird.NudebirdPostExtractor.pattern,
    "#count"   : ">=52",

    "tag_slug": "dead-or-alive"
},

{
    "#url"     : "https://nudebird.biz/cosermeenfox-marie-rose-fortune-18-42-photos-1-video/",
    "#class"   : nudebird.NudebirdPostExtractor,
    "#pattern" : r"https://nudebird\.biz/wp\-content/uploads/\d{4}/\d{2}/\d+\-\d+\.(?:webp|jpg|jpeg|png)",
    "#count"   : 42,

    "count"         : 42,
    "date_published": "dt:2025-05-24 00:00:00",
    "extension"     : "webp",
    "gallery_id"    : "cosermeenfox-marie-rose-fortune-18-42-photos-1-video",
    "post_category" : "Hentai Cosplay",
    "post_slug"     : "cosermeenfox-marie-rose-fortune-18-42-photos-1-video",
    "post_url"      : "https://nudebird.biz/cosermeenfox-marie-rose-fortune-18-42-photos-1-video/",
    "tags"          : ["hentai cosplay"],
    "title"         : "Coser@MeenFox: Marie Rose Fortune 18+ (42 photos + 1 video)",
},

{
    "#url"     : "https://nudebird.biz/?s=Marie+Rose",
    "#class"   : nudebird.NudebirdSearchExtractor,
    "#pattern" : nudebird.NudebirdPostExtractor.pattern,
    "#count"   : ">=47",

    "search_query": "Marie+Rose"
},

{
    "#url"     : "https://nudebird.biz/most-popular-weekly/",
    "#class"   : nudebird.NudebirdPopularExtractor,
    "#pattern" : nudebird.NudebirdPostExtractor.pattern,
    "#range"   : "150-250",

    "popularity_period": "weekly"
},

)
