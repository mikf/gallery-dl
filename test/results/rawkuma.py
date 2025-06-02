# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import rawkuma


__tests__ = (
{
    "#url"     : "https://rawkuma.net/hitman-chapter-127/",
    "#class"   : rawkuma.RawkumaChapterExtractor,
    "#pattern" : r"https://cdn.kumacdn.club/wp-content/uploads/images/h/hitman/chapter-127/.+\.jpg$",
    "#count"   : 18,

    "chapter"      : 127,
    "chapter_id"   : 313750,
    "chapter_minor": "",
    "count"        : 18,
    "date"         : "dt:2021-07-01 07:07:27",
    "extension"    : "jpg",
    "filename"     : str,
    "lang"         : "ja",
    "language"     : "Japanese",
    "manga"        : "Hitman",
    "manga_id"     : 47920,
    "page"         : range(1, 18),
    "thumbnail"    : "https://rawkuma.net/wp-content/uploads/2020/10/Hitman-10.jpg",
    "title"        : "End",
},

{
    "#url"     : "https://rawkuma.net/saikyou-inyoushi-no-isekai-tenseiki-chapter-8-1/",
    "#class"   : rawkuma.RawkumaChapterExtractor,
    "#pattern" : r"https://cdn.kumacdn.club/wp-content/uploads/images/s/saikyou-inyoushi-no-isekai-tenseiki/chapter-8-1/.+\.jpg$",

    "chapter"      : 8,
    "chapter_id"   : 85076,
    "chapter_minor": ".1",
    "count"        : 11,
    "date"         : "dt:2023-11-21 06:27:19",
    "extension"    : "jpg",
    "filename"     : str,
    "lang"         : "ja",
    "language"     : "Japanese",
    "manga"        : "Saikyou Inyoushi no Isekai Tenseiki",
    "manga_id"     : 20781,
    "page"         : range(1, 11),
    "thumbnail"    : "https://rawkuma.net/wp-content/uploads/2020/06/Saikyou-Inyoushi-no-Isekai-Tenseiki-cover.jpg",
    "title"        : "",
},

{
    "#url"     : "https://rawkuma.net/manga/hitman/",
    "#class"   : rawkuma.RawkumaMangaExtractor,
    "#pattern" : rawkuma.RawkumaChapterExtractor.pattern,

    "chapter"      : range(1, 127),
    "chapter-minor": {"", ".5"},
    "manga"        : "Hitman",
    "title"        : {"", "End"},
},

)
