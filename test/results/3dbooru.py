# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.3dbooru")
_3dbooru = getattr(gallery_dl.extractor, "3dbooru")


__tests__ = (
{
    "#url"     : "http://behoimi.org/post?tags=himekawa_azuru+dress",
    "#category": ("booru", "3dbooru", "tag"),
    "#class"   : _3dbooru._3dbooruTagExtractor,
    "#sha1_url"    : "ecb30c6aaaf8a6ff8f55255737a9840832a483c1",
    "#sha1_content": "11cbda40c287e026c1ce4ca430810f761f2d0b2a",
},

{
    "#url"     : "http://behoimi.org/pool/show/27",
    "#category": ("booru", "3dbooru", "pool"),
    "#class"   : _3dbooru._3dbooruPoolExtractor,
    "#sha1_url"    : "da75d2d1475449d5ef0c266cb612683b110a30f2",
    "#sha1_content": "fd5b37c5c6c2de4b4d6f1facffdefa1e28176554",
},

{
    "#url"     : "http://behoimi.org/post/show/140852",
    "#category": ("booru", "3dbooru", "post"),
    "#class"   : _3dbooru._3dbooruPostExtractor,
    "#options"     : {"tags": True},
    "#sha1_url"    : "ce874ea26f01d6c94795f3cc3aaaaa9bc325f2f6",
    "#sha1_content": "26549d55b82aa9a6c1686b96af8bfcfa50805cd4",

    "tags_character": "furude_rika",
    "tags_copyright": "higurashi_no_naku_koro_ni",
    "tags_model"    : "himekawa_azuru",
    "tags_general"  : str,
},

{
    "#url"     : "http://behoimi.org/post/popular_by_month?month=2&year=2013",
    "#category": ("booru", "3dbooru", "popular"),
    "#class"   : _3dbooru._3dbooruPopularExtractor,
    "#pattern" : r"http://behoimi\.org/data/../../[0-9a-f]{32}\.jpg",
    "#count"   : 20,
},

)
