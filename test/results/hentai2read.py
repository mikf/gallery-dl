# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentai2read


__tests__ = (
{
    "#url"     : "https://hentai2read.com/amazon_elixir/1/",
    "#category": ("", "hentai2read", "chapter"),
    "#class"   : hentai2read.Hentai2readChapterExtractor,
    "#sha1_url"     : "964b942cf492b3a129d2fe2608abfc475bc99e71",
    "#sha1_metadata": "85645b02d34aa11b3deb6dadd7536863476e1bad",
},

{
    "#url"     : "https://hentai2read.com/popuni_kei_joshi_panic/2.5/",
    "#category": ("", "hentai2read", "chapter"),
    "#class"   : hentai2read.Hentai2readChapterExtractor,
    "#pattern" : r"https://hentaicdn\.com/hentai/13088/2\.5y/ccdn00\d+\.jpg",
    "#count"   : 36,

    "author"       : "Kurisu",
    "chapter"      : 2,
    "chapter_id"   : 75152,
    "chapter_minor": ".5",
    "count"        : 36,
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Popuni Kei Joshi Panic!",
    "manga_id"     : 13088,
    "page"         : int,
    "title"        : "Popuni Kei Joshi Panic! 2.5",
    "type"         : "Original",
},

{
    "#url"     : "https://hentai2read.com/amazon_elixir/",
    "#category": ("", "hentai2read", "manga"),
    "#class"   : hentai2read.Hentai2readMangaExtractor,
    "#sha1_url"     : "273073752d418ec887d7f7211e42b832e8c403ba",
    "#sha1_metadata": "5c1b712258e78e120907121d3987c71f834d13e1",
},

{
    "#url"     : "https://hentai2read.com/oshikage_riot/",
    "#category": ("", "hentai2read", "manga"),
    "#class"   : hentai2read.Hentai2readMangaExtractor,
    "#sha1_url"     : "6595f920a3088a15c2819c502862d45f8eb6bea6",
    "#sha1_metadata": "a2e9724acb221040d4b29bf9aa8cb75b2240d8af",
},

{
    "#url"     : "https://hentai2read.com/popuni_kei_joshi_panic/",
    "#category": ("", "hentai2read", "manga"),
    "#class"   : hentai2read.Hentai2readMangaExtractor,
    "#pattern" : hentai2read.Hentai2readChapterExtractor.pattern,
    "#range"   : "2-3",

    "chapter"      : int,
    "chapter_id"   : int,
    "chapter_minor": ".5",
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Popuni Kei Joshi Panic!",
    "manga_id"     : 13088,
    "title"        : str,
    "type"         : "Original",
},

)
