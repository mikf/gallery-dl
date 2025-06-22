# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import comicfury


__tests__ = (
{
    "#url"     : "https://rain.thecomicseries.com/comics/pl/73003",
    "#category": ("", "comicfury", "issue"),
    "#class"   : comicfury.ComicfuryIssueExtractor,
    "#count"   : 1,
    "#urls"    : "https://img.comicfury.com/comics/c8f813e19a0aae0f2a0b57a6b36ceec52058036413.png",

    "comic_name"  : "Rain",
    "comic"       : "rain",
    "relative_id" : 6,
    "id"          : 73003,
    "chapter_id"  : 2770,
    "chapter_name": "Ch 1: The New Girl",
    "title"       : "Chapter 1 - The New Girl",
},

{
    "#url"     : "https://grinders.the-comic.org/comics/first",
    "#category": ("", "comicfury", "issue"),
    "#class"   : comicfury.ComicfuryIssueExtractor,
    "#count"   : 1,
    "#urls"    : "https://img.comicfury.com/comics/184/43571a1579840219f1635377961.png",

    "comic_name"  : "Grinder$",
    "comic"       : "grinders",
    "relative_id" : 1,
    "id"          : 1137093,
    "chapter_id"  : 48527,
    "chapter_name": "Foam",
    "title"       : "Teaser",
},

{
    "#url"     : "https://belovedchainscomic.thecomicstrip.org/comics/1",
    "#category": ("", "comicfury", "issue"),
    "#class"   : comicfury.ComicfuryIssueExtractor,
},

{
    "#url"     : "https://belovedchainscomic.webcomic.ws/comics/",
    "#category": ("", "comicfury", "issue"),
    "#class"   : comicfury.ComicfuryIssueExtractor,
},

{
    "#url"     : "https://comicfury.com/read/MKsJekyllAndHyde/comic/last",
    "#category": ("", "comicfury", "issue"),
    "#class"   : comicfury.ComicfuryIssueExtractor,
    "#count"   : 1,
    "#urls"    : "https://img.comicfury.com/comics/222/37111a1634996413b60163f1077624721.png",

    "comic_name"  : "MK's The Strange Case of Dr. Jekyll and Mr. Hyde",
    "comic"       : "MKsJekyllAndHyde",
    "relative_id" : 622,
    "id"          : 1493321,
    "chapter_id"  : 57040,
    "chapter_name": "Epilogue 3",
    "title"       : "THE END",
},

{
    "#url"     : "https://comicfury.com/read/rain-tradfr",
    "#category": ("", "comicfury", "issue"),
    "#class"   : comicfury.ComicfuryIssueExtractor,
    "#count"   : 1,
    "#urls"    : "https://img.comicfury.com/comics/218/49338a1624179795b80143f379314885.jpg",

    "comic_name"  : "Rain, la traduction française",
    "comic"       : "rain-tradfr",
    "relative_id" : 1,
    "id"          : 1381699,
    "chapter_id"  : 56171,
    "chapter_name": "Hors Chapitre",
    "title"       : "RAIN",
},

{
    "#url"     : "https://comicfury.com/comicprofile.php?url=lanternsofarcadia",
    "#category": ("", "comicfury", "comic"),
    "#class"   : comicfury.ComicfuryComicExtractor,
    "#range"   : "1-6",
    "#sha1_url"    : "d4080dcb41f5c019e1ceb450a624041208ccdcb8",
    "#sha1_content": "0c1937e4d177ce55afbfe30ab9376700c6cf619f",
},

{
    "#url"     : "https://bloomer-layout.cfw.me",
    "#category": ("", "comicfury", "comic"),
    "#class"   : comicfury.ComicfuryComicExtractor,
},

)
