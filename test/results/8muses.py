# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.8muses")
_8muses = getattr(gallery_dl.extractor, "8muses")
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://comics.8muses.com/comics/album/Fakku-Comics/mogg/Liar",
    "#category": ("", "8muses", "album"),
    "#class"   : _8muses._8musesAlbumExtractor,
    "#pattern" : r"https://comics.8muses.com/image/fl/[\w-]+",
    "#sha1_url": "6286ac33087c236c5a7e51f8a9d4e4d5548212d4",

    "url"  : str,
    "hash" : str,
    "page" : int,
    "count": 6,
    "album": {
        "id"     : 10467,
        "title"  : "Liar",
        "path"   : "Fakku Comics/mogg/Liar",
        "parts"  : [
            "Fakku Comics",
            "mogg",
            "Liar",
        ],
        "private": False,
        "url"    : "https://comics.8muses.com/comics/album/Fakku-Comics/mogg/Liar",
        "parent" : 10464,
        "views"  : int,
        "likes"  : int,
        "date"   : "dt:2018-07-10 00:00:00",
    },
},

{
    "#url"     : "https://www.8muses.com/comics/album/Fakku-Comics/santa",
    "#category": ("", "8muses", "album"),
    "#class"   : _8muses._8musesAlbumExtractor,
    "#pattern" : _8muses._8musesAlbumExtractor.pattern,
    "#count"   : ">= 3",

    "url"    : str,
    "name"   : str,
    "private": False,
},

{
    "#url"     : "https://www.8muses.com/comics/album/Fakku-Comics/11?sort=az",
    "#comment" : "custom sorting",
    "#category": ("", "8muses", "album"),
    "#class"   : _8muses._8musesAlbumExtractor,
    "#count"   : ">= 70",

    "name": r"re:^[R-Zr-z]",
},

{
    "#url"     : "https://comics.8muses.com/comics/album/Various-Authors/Chessire88/From-Trainers-to-Pokmons",
    "#comment" : "non-ASCII characters",
    "#category": ("", "8muses", "album"),
    "#class"   : _8muses._8musesAlbumExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://comics.8muses.com/comics/album/Tufos-Comics/Gallery",
    "#comment" : "private albums without 'permalink' (#6717)",
    "#category": ("", "8muses", "album"),
    "#class"   : _8muses._8musesAlbumExtractor,
    "#count"   : range(100, 150),
},

)
