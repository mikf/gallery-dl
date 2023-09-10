# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentaihere


__tests__ = (
{
    "#url"     : "https://hentaihere.com/m/S13812/1/1/",
    "#category": ("", "hentaihere", "chapter"),
    "#class"   : hentaihere.HentaihereChapterExtractor,
    "#sha1_url"     : "964b942cf492b3a129d2fe2608abfc475bc99e71",
    "#sha1_metadata": "0207d20eea3a15d2a8d1496755bdfa49de7cfa9d",
},

{
    "#url"     : "https://hentaihere.com/m/S23048/1.5/1/",
    "#category": ("", "hentaihere", "chapter"),
    "#class"   : hentaihere.HentaihereChapterExtractor,
    "#pattern" : r"https://hentaicdn\.com/hentai/23048/1\.5/ccdn00\d+\.jpg",
    "#count"   : 32,

    "author"       : "Shinozuka Yuuji",
    "chapter"      : 1,
    "chapter_id"   : 80186,
    "chapter_minor": ".5",
    "count"        : 32,
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "High School Slut's Love Consultation",
    "manga_id"     : 23048,
    "page"         : int,
    "title"        : "High School Slut's Love Consultation + Girlfriend [Full Color]",
    "type"         : "Original",
},

{
    "#url"     : "https://hentaihere.com/m/S13812",
    "#category": ("", "hentaihere", "manga"),
    "#class"   : hentaihere.HentaihereMangaExtractor,
    "#sha1_url"     : "d1ba6e28bb2162e844f8559c2b2725ba0a093559",
    "#sha1_metadata": "5c1b712258e78e120907121d3987c71f834d13e1",
},

{
    "#url"     : "https://hentaihere.com/m/S7608",
    "#category": ("", "hentaihere", "manga"),
    "#class"   : hentaihere.HentaihereMangaExtractor,
    "#sha1_url": "6c5239758dc93f6b1b4175922836c10391b174f7",

    "chapter"      : int,
    "chapter_id"   : int,
    "chapter_minor": "",
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Oshikake Riot",
    "manga_id"     : 7608,
    "title"        : r"re:Oshikake Riot( \d+)?",
    "type"         : "Original",
},

)
