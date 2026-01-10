# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import dankefuerslesen


__tests__ = (
{
    "#url"     : "https://danke.moe/read/manga/awana-chan-wa-kyou-mo-shiawase/2/1/",
    "#class"   : dankefuerslesen.DankefuerslesenChapterExtractor,
    "#pattern" : r"https://danke.moe/media/manga/awana-chan-wa-kyou-mo-shiawase/chapters/0002_m9inbehz/69/\d+\.png",
    "#count"   : 22,

    "volume"    : 1,
    "chapter"   : 2,
    "chapter_minor": "",
    "count"     : 22,
    "page"      : range(1, 22),
    "date"      : "dt:2025-02-09 19:03:08",
    "extension" : "png",
    "filename"  : str,
    "group"     : ["Good Try Scans"],
    "group_id"  : 69,
    "lang"      : None,
    "language"  : None,
    "manga"     : "Awana-chan wa Kyou mo Shiawase",
    "manga_slug": "awana-chan-wa-kyou-mo-shiawase",
    "title"     : "Eat some ramen!",
    "artist"    : "Tabayou",
    "author"    : "Tabayou",
    "description": "<p>A convenience store part-timer who can't seem to do anything right: Awana-chan. Today, yet again, she messed up over and over, and she can't even count how many times she was told off... How will Awana-chan find happiness in a situation like this, without anyone else to rely on!? This is a manga about creating your own happiness!!</p>",
},

{
    "#url"     : "https://danke.moe/read/manga/awana-chan-wa-kyou-mo-shiawase/2/1/",
    "#comment" : "ZIP archive download",
    "#class"   : dankefuerslesen.DankefuerslesenChapterExtractor,
    "#options" : {"zip": True},
    "#results" : "https://danke.moe/api/download_chapter/awana-chan-wa-kyou-mo-shiawase/2/",

    "count"    : 0,
    "page"     : 0,
    "extension": "zip",
},

{
    "#url"     : "https://danke.moe/read/manga/raul-and-the-vampire/7-5/1/",
    "#comment" : "minor chapter version",
    "#class"   : dankefuerslesen.DankefuerslesenChapterExtractor,
    "#pattern" : r"https://danke.moe/media/manga/raul-and-the-vampire/chapters/0009-5_efnaqvlj/56/\d+\.png",
    "#count"   : 20,

    "volume"    : 1,
    "chapter"   : 7,
    "chapter_minor": ".5",
    "count"     : 20,
    "page"      : range(1, 20),
    "date"      : "dt:2024-10-10 07:12:44",
    "extension" : "png",
    "filename"  : str,
    "group"     : ["Danke fürs Lesen", "Senko-san's Abode"],
    "group_id"  : 56,
    "lang"      : None,
    "language"  : None,
    "manga"     : "Raul and The Vampire",
    "manga_slug": "raul-and-the-vampire",
    "title"     : "Volume 1 Extras",
    "artist"    : "Sonoguchi Naka",
    "author"    : "Sonoguchi Naka",
    "description": "<a href=\"https://twitter.com/2525_25_25_25_\"><img src=\"https://i.imgur.com/dQCXZkU.png\" alt=\"twitter\"/>Artist's Twitter</a>\r\n<a href=\"https://www.pixiv.net/en/users/67164428\"><img src=\"https://i.imgur.com/oiVINmy.png\" alt=\"pixiv\"/>Artist's Pixiv</a>",
},

{
    "#url"     : "https://danke.moe/read/series/awana-chan-wa-kyou-mo-shiawase/2/1/",
    "#class"   : dankefuerslesen.DankefuerslesenChapterExtractor,
},

{
    "#url"     : "https://danke.moe/reader/manga/awana-chan-wa-kyou-mo-shiawase/2/1/",
    "#class"   : dankefuerslesen.DankefuerslesenChapterExtractor,
},

{
    "#url"     : "https://danke.moe/reader/series/awana-chan-wa-kyou-mo-shiawase/2/1/",
    "#class"   : dankefuerslesen.DankefuerslesenChapterExtractor,
},

{
    "#url"     : "https://danke.moe/read/manga/awana-chan-wa-kyou-mo-shiawase/",
    "#class"   : dankefuerslesen.DankefuerslesenMangaExtractor,
    "#pattern" : dankefuerslesen.DankefuerslesenChapterExtractor.pattern,
    "#results" : (
        "https://danke.moe/read/manga/awana-chan-wa-kyou-mo-shiawase/1/1/",
        "https://danke.moe/read/manga/awana-chan-wa-kyou-mo-shiawase/2/1/",
        "https://danke.moe/read/manga/awana-chan-wa-kyou-mo-shiawase/3/1/",
        "https://danke.moe/read/manga/awana-chan-wa-kyou-mo-shiawase/4/1/",
    ),

    "chapter" : range(1, 4),
    "chapter_minor": "",
    "lang"    : None,
    "language": None,
},

{
    "#url"     : "https://danke.moe/read/series/awana-chan-wa-kyou-mo-shiawase",
    "#class"   : dankefuerslesen.DankefuerslesenMangaExtractor,
},

{
    "#url"     : "https://danke.moe/reader/manga/awana-chan-wa-kyou-mo-shiawase",
    "#class"   : dankefuerslesen.DankefuerslesenMangaExtractor,
},

{
    "#url"     : "https://danke.moe/reader/series/awana-chan-wa-kyou-mo-shiawase",
    "#class"   : dankefuerslesen.DankefuerslesenMangaExtractor,
},

)
