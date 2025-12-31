# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import manganelo
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.nelomanga.net/manga/danzai-sareta-akuyaku-reijou-wa-gyakkou-shite-kanpeki-na-akujo-wo-mezasu/chapter-4-5",
    "#category": ("manganelo", "nelomanga", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
    "#pattern" : r"https://imgs-2.2xstorage.com/danzai-sareta-akuyaku-reijou-wa-gyakkou-shite-kanpeki-na-akujo-wo-mezasu/4\.5/\d+\.webp",
    "#count"   : 24,

    "author"       : "NARAYAMA Bakufu",
    "chapter"      : 4,
    "chapter_id"   : 6,
    "chapter_minor": ".5",
    "count"        : 24,
    "date"         : "",
    "date_updated" : "",
    "extension"    : "webp",
    "filename"     : str,
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Danzai sareta Akuyaku Reijou wa, Gyakkou shite Kanpeki na Akujo wo Mezasu",
    "manga_id"     : 32842,
    "page"         : range(1, 24),
},

{
    "#url"     : "https://nelomanga.net/manga/aria/chapter-60-2",
    "#category": ("manganelo", "nelomanga", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
},

{
    "#url"     : "https://www.nelomanga.net/manga/aria",
    "#category": ("manganelo", "nelomanga", "manga"),
    "#class"   : manganelo.ManganeloMangaExtractor,
    "#pattern" : manganelo.ManganeloChapterExtractor.pattern,
    "#count"   : 70,

    "author"  : "Amano Kozue",
    "chapter" : range(1, 60),
    "chapter_minor": {"", ".1", ".2", ".5"},
    "date"    : "type:datetime",
    "date_updated": "dt:2024-10-30 17:20:58",
    "lang"    : "en",
    "language": "English",
    "manga"   : "Aria",
    "status"  : "Completed",
    "title"   : "",
    "tags": [
        "Adventure",
        "Comedy",
        "Drama",
        "Sci fi",
        "Shounen",
        "Slice of life",
    ],
},

{
    "#url"     : "https://nelomanga.net/manga/aria",
    "#category": ("manganelo", "nelomanga", "manga"),
    "#class"   : manganelo.ManganeloMangaExtractor,
},

{
    "#url"     : "https://www.nelomanga.net/bookmark",
    "#category": ("manganelo", "nelomanga", "bookmark"),
    "#class"   : manganelo.ManganeloBookmarkExtractor,
    "#pattern" : manganelo.ManganeloMangaExtractor.pattern,
    "#auth"    : "cookies",
    "#count"   : 23,
},

{
    "#url"     : "https://nelomanga.net/bookmark",
    "#category": ("manganelo", "nelomanga", "bookmark"),
    "#class"   : manganelo.ManganeloBookmarkExtractor,
    "#auth"     : False,
    "#exception": exception.AuthRequired,
},

)
