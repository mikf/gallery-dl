# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import webtoons
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.webtoons.com/en/comedy/safely-endangered/ep-572-earth/viewer?title_no=352&episode_no=572",
    "#category": ("", "webtoons", "episode"),
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#count"       : 5,
    "#sha1_url"    : "55bec5d7c42aba19e3d0d56db25fdf0b0b13be38",
    "#sha1_content": [
        "1748c7e82b6db910fa179f6dc7c4281b0f680fa7",
        "42055e44659f6ffc410b3fb6557346dfbb993df3",
        "49e1f2def04c6f7a6a3dacf245a1cd9abe77a6a9",
    ],
},

{
    "#url"     : "https://www.webtoons.com/en/challenge/punderworld/happy-earth-day-/viewer?title_no=312584&episode_no=40",
    "#category": ("", "webtoons", "episode"),
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#exception": exception.NotFoundError,

    "comic"      : "punderworld",
    "description": str,
    "episode"    : "36",
    "episode_no" : "40",
    "genre"      : "challenge",
    "title"      : r"re:^Punderworld - .+",
    "title_no"   : "312584",
},

{
    "#url"     : "https://www.webtoons.com/en/comedy/live-with-yourself/list?title_no=919",
    "#comment" : "english",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
    "#pattern" : webtoons.WebtoonsEpisodeExtractor.pattern,
    "#range"   : "1-15",
    "#count"   : ">= 15",
},

{
    "#url"     : "https://www.webtoons.com/fr/romance/subzero/list?title_no=1845&page=3",
    "#comment" : "french",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
    "#count"   : ">= 15",
},

{
    "#url"     : "https://www.webtoons.com/en/challenge/scoob-and-shag/list?title_no=210827&page=9",
    "#comment" : "(#820)",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
    "#count"   : ">= 18",
},

{
    "#url"     : "https://www.webtoons.com/es/romance/lore-olympus/list?title_no=1725",
    "#comment" : "(#1643)",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
},

)
