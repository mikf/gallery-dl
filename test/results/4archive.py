# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.4archive")
_4archive = getattr(gallery_dl.extractor, "4archive")


__tests__ = (
{
    "#url"     : "https://4archive.org/board/u/thread/2397221",
    "#category": ("", "4archive", "thread"),
    "#class"   : _4archive._4archiveThreadExtractor,
    "#pattern" : r"https://(cdn\.4archive\.org/u/image/150\d/\d\d\d/\d+\.\w+|4archive\.org/image/image-404\.png)",
    "#count"   : 16,

    "board" : "u",
    "com"   : str,
    "date"  : "type:datetime",
    "name"  : "Anonymous",
    "no"    : range(2397221, 2418158),
    "thread": 2397221,
    "time"  : int,
    "title" : "best anime",
    "url"   : str,
    "width" : int,
    "height": int,
    "size"  : int,
},

{
    "#url"     : "https://4archive.org/board/jp/thread/17611798",
    "#category": ("", "4archive", "thread"),
    "#class"   : _4archive._4archiveThreadExtractor,
    "#pattern" : r"https://(cdn\.4archive\.org/jp/image/\d\d\d\d/\d\d\d/\d+\.\w+|4archive\.org/image/image-404\.png)",
    "#count"   : 85,
},

{
    "#url"     : "https://4archive.org/board/u",
    "#category": ("", "4archive", "board"),
    "#class"   : _4archive._4archiveBoardExtractor,
    "#pattern" : _4archive._4archiveThreadExtractor.pattern,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://4archive.org/board/jp/10",
    "#category": ("", "4archive", "board"),
    "#class"   : _4archive._4archiveBoardExtractor,
    "#pattern" : _4archive._4archiveThreadExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
}

)
