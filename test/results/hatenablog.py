# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hatenablog


__tests__ = (
{
    "#url"     : "https://cosmiclatte.hatenablog.com/entry/2020/05/28/003227",
    "#category": ("", "hatenablog", "entry"),
    "#class"   : hatenablog.HatenablogEntryExtractor,
    "#count"   : 20,
},

{
    "#url"     : "https://moko0908.hatenablog.jp/entry/2023/12/31/083846",
    "#category": ("", "hatenablog", "entry"),
    "#class"   : hatenablog.HatenablogEntryExtractor,
},

{
    "#url"     : "https://p-shirokuma.hatenadiary.com/entry/20231227/1703685600",
    "#category": ("", "hatenablog", "entry"),
    "#class"   : hatenablog.HatenablogEntryExtractor,
},

{
    "#url"     : "https://urakatahero.hateblo.jp/entry/2ndlife",
    "#category": ("", "hatenablog", "entry"),
    "#class"   : hatenablog.HatenablogEntryExtractor,
},

{
    "#url"     : "hatenablog:https://blog.hyouhon.com/entry/2023/12/22/133549",
    "#category": ("", "hatenablog", "entry"),
    "#class"   : hatenablog.HatenablogEntryExtractor,
},

{
    "#url"     : "https://cetriolo.hatenablog.com",
    "#category": ("", "hatenablog", "home"),
    "#class"   : hatenablog.HatenablogHomeExtractor,
    "#range"   : "1-7",
    "#count"   : 7,
},

{
    "#url"     : "https://moko0908.hatenablog.jp/",
    "#category": ("", "hatenablog", "home"),
    "#class"   : hatenablog.HatenablogHomeExtractor,
},

{
    "#url"     : "https://p-shirokuma.hatenadiary.com/",
    "#category": ("", "hatenablog", "home"),
    "#class"   : hatenablog.HatenablogHomeExtractor,
},

{
    "#url"     : "https://urakatahero.hateblo.jp/",
    "#category": ("", "hatenablog", "home"),
    "#class"   : hatenablog.HatenablogHomeExtractor,
},

{
    "#url"     : "hatenablog:https://blog.hyouhon.com/",
    "#category": ("", "hatenablog", "home"),
    "#class"   : hatenablog.HatenablogHomeExtractor,
},

{
    "#url"     : ("https://8saki.hatenablog.com/archive/category/%E3%82%BB%E3"
                  "%83%AB%E3%83%95%E3%82%B8%E3%82%A7%E3%83%AB%E3%83%8D%E3%82"
                  "%A4%E3%83%AB"),
    "#category": ("", "hatenablog", "archive"),
    "#class"   : hatenablog.HatenablogArchiveExtractor,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://moko0908.hatenablog.jp/archive/2023",
    "#category": ("", "hatenablog", "archive"),
    "#class"   : hatenablog.HatenablogArchiveExtractor,
    "#count"   : range(10, 15),
},

{
    "#url"     : "https://p-shirokuma.hatenadiary.com/archive/2023/01",
    "#category": ("", "hatenablog", "archive"),
    "#class"   : hatenablog.HatenablogArchiveExtractor,
    "#count"   : 5,
},

{
    "#url"     : "https://urakatahero.hateblo.jp/archive",
    "#category": ("", "hatenablog", "archive"),
    "#class"   : hatenablog.HatenablogArchiveExtractor,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "hatenablog:https://blog.hyouhon.com/archive/2024/01/01",
    "#category": ("", "hatenablog", "archive"),
    "#class"   : hatenablog.HatenablogArchiveExtractor,
},

{
    "#url"     : "hatenablog:https://blog.hyouhon.com/search?q=a",
    "#category": ("", "hatenablog", "search"),
    "#class"   : hatenablog.HatenablogSearchExtractor,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://cosmiclatte.hatenablog.com/search?q=a",
    "#category": ("", "hatenablog", "search"),
    "#class"   : hatenablog.HatenablogSearchExtractor,
},

{
    "#url"     : "https://moko0908.hatenablog.jp/search?q=a",
    "#category": ("", "hatenablog", "search"),
    "#class"   : hatenablog.HatenablogSearchExtractor,
},

{
    "#url"     : "https://p-shirokuma.hatenadiary.com/search?q=a",
    "#category": ("", "hatenablog", "search"),
    "#class"   : hatenablog.HatenablogSearchExtractor,
},

{
    "#url"     : "https://urakatahero.hateblo.jp/search?q=a",
    "#category": ("", "hatenablog", "search"),
    "#class"   : hatenablog.HatenablogSearchExtractor,
},

)
