# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import manganelo


__tests__ = (
{
    "#url"     : "https://chapmanganato.com/manga-gn983696/chapter-23",
    "#category": ("", "manganelo", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
    "#pattern"      : r"https://v\d+\.mkklcdnv6tempv5\.com/img/tab_17/03/23/39/gn983696/vol_3_chapter_23_24_yen/\d+-[no]\.jpg",
    "#count"        : 25,

    "author"   : "Ei Yuzuki,Maki Hayashi",
    "chapter"  : 23,
    "chapter_minor": "",
    "count"    : 25,
    "date"     : None,
    "extension": "jpg",
    "filename" : str,
    "lang"     : "en",
    "language" : "English",
    "manga"    : "By Spring",
    "page"     : range(1, 25),
    "title"    : "24 Yen",
    "volume"   : 3,
},

{
    "#url"     : "https://chapmanganelo.com/manga-ti107776/chapter-4",
    "#category": ("", "manganelo", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
    "#pattern"      : r"https://v\d+\.mkklcdnv6tempv5\.com/img/tab_17/01/92/08/ti970565/chapter_4_caster/\d+-o\.jpg",
    "#count"        : 45,
    "#sha1_metadata": "06e01fa9b3fc9b5b954c0d4a98f0153b40922ded",
},

{
    "#url"     : "https://chapmanganato.com/manga-no991297/chapter-8",
    "#category": ("", "manganelo", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
    "#count"   : 20,

    "chapter"      : 8,
    "chapter_minor": "-1",
},

{
    "#url"     : "https://readmanganato.com/manga-gn983696/chapter-23",
    "#category": ("", "manganelo", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
},

{
    "#url"     : "https://manganelo.com/chapter/gamers/chapter_15",
    "#category": ("", "manganelo", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
},

{
    "#url"     : "https://manganelo.com/chapter/gq921227/chapter_23",
    "#category": ("", "manganelo", "chapter"),
    "#class"   : manganelo.ManganeloChapterExtractor,
},

{
    "#url"     : "https://chapmanganato.com/manga-gn983696",
    "#category": ("", "manganelo", "manga"),
    "#class"   : manganelo.ManganeloMangaExtractor,
    "#pattern" : manganelo.ManganeloChapterExtractor.pattern,
    "#count"   : ">= 25",
},

{
    "#url"     : "https://m.manganelo.com/manga-ti107776",
    "#category": ("", "manganelo", "manga"),
    "#class"   : manganelo.ManganeloMangaExtractor,
    "#pattern" : manganelo.ManganeloChapterExtractor.pattern,
    "#count"   : ">= 12",
},

{
    "#url"     : "https://readmanganato.com/manga-gn983696",
    "#category": ("", "manganelo", "manga"),
    "#class"   : manganelo.ManganeloMangaExtractor,
},

{
    "#url"     : "https://manganelo.com/manga/read_otome_no_teikoku",
    "#category": ("", "manganelo", "manga"),
    "#class"   : manganelo.ManganeloMangaExtractor,
},

{
    "#url"     : "https://manganelo.com/manga/ol921234/",
    "#category": ("", "manganelo", "manga"),
    "#class"   : manganelo.ManganeloMangaExtractor,
},

)
