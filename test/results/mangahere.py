# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangahere


__tests__ = (
{
    "#url"     : "https://www.mangahere.cc/manga/dongguo_xiaojie/c004.2/",
    "#category": ("", "mangahere", "chapter"),
    "#class"   : mangahere.MangahereChapterExtractor,
    "#sha1_metadata": "7c98d7b50a47e6757b089aa875a53aa970cac66f",
    "#sha1_content" : "708d475f06893b88549cbd30df1e3f9428f2c884",
},

{
    "#url"     : "https://www.mangahere.cc/manga/beastars/c196/1.html",
    "#comment" : "URLs without HTTP scheme (#1070)",
    "#category": ("", "mangahere", "chapter"),
    "#class"   : mangahere.MangahereChapterExtractor,
    "#pattern" : "https://zjcdn.mangahere.org/.*",
},

{
    "#url"     : "http://www.mangahere.co/manga/dongguo_xiaojie/c003.2/",
    "#category": ("", "mangahere", "chapter"),
    "#class"   : mangahere.MangahereChapterExtractor,
},

{
    "#url"     : "http://m.mangahere.co/manga/dongguo_xiaojie/c003.2/",
    "#category": ("", "mangahere", "chapter"),
    "#class"   : mangahere.MangahereChapterExtractor,
},

{
    "#url"     : "https://www.mangahere.cc/manga/aria/",
    "#category": ("", "mangahere", "manga"),
    "#class"   : mangahere.MangahereMangaExtractor,
    "#count"        : 71,
    "#sha1_url"     : "9c2e54ec42e9a87ad53096c328b33c90750af3e4",
    "#sha1_metadata": "71503c682c5d0c277a50409a8c5fd78e871e3d69",
},

{
    "#url"     : "https://www.mangahere.cc/manga/hiyokoi/#50",
    "#category": ("", "mangahere", "manga"),
    "#class"   : mangahere.MangahereMangaExtractor,
    "#sha1_url"     : "654850570aa03825cd57e2ae2904af489602c523",
    "#sha1_metadata": "c8084d89a9ea6cf40353093669f9601a39bf5ca2",
},

{
    "#url"     : "http://www.mangahere.cc/manga/gunnm_mars_chronicle/",
    "#comment" : "adult filter (#556)",
    "#category": ("", "mangahere", "manga"),
    "#class"   : mangahere.MangahereMangaExtractor,
    "#pattern" : mangahere.MangahereChapterExtractor.pattern,
    "#count"   : ">= 50",
},

{
    "#url"     : "https://www.mangahere.co/manga/aria/",
    "#category": ("", "mangahere", "manga"),
    "#class"   : mangahere.MangahereMangaExtractor,
},

{
    "#url"     : "https://m.mangahere.co/manga/aria/",
    "#category": ("", "mangahere", "manga"),
    "#class"   : mangahere.MangahereMangaExtractor,
},

)
