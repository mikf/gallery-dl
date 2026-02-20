# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import toongod


__tests__ = (
{
    "#url"     : "https://www.toongod.org/webtoon/a-million-sub-gym-influencer-becomes-a-webtoon-loser/chapter-1/",
    "#class"   : toongod.ToongodChapterExtractor,
    "#pattern" : r"https://i\.tngcdn\.com/manga_\d+/\d+/\d+\.webp",
    "#count"   : 16,

    "chapter"      : 1,
    "chapter_minor": "",
    "slug"         : "a-million-sub-gym-influencer-becomes-a-webtoon-loser",
    "count"        : 16,
    "page"         : range(1, 16),
},

{
    "#url"     : "https://www.toongod.org/webtoon/a-million-sub-gym-influencer-becomes-a-webtoon-loser/",
    "#class"   : toongod.ToongodWebtoonExtractor,
    "#pattern" : toongod.ToongodChapterExtractor.pattern,
    "#count"   : range(1, 20),

    "chapter"      : range(1, 20),
    "chapter_minor": "",
},

)
