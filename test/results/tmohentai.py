# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tmohentai


__tests__ = (
{
    "#url"     : "https://tmohentai.com/contents/653c2aeaa693c",
    "#category": ("", "tmohentai", "gallery"),
    "#class"   : tmohentai.TmohentaiGalleryExtractor,
    "#pattern" : r"https://imgrojo\.tmohentai\.com/contents/653c2aeaa693c/\d\d\d\.webp",
    "#count"   : 46,

    "artists"   : ["Andoryu"],
    "genres"    : [
        "Big Breasts",
        "BlowJob",
        "Cheating",
        "Mature",
        "Milf",
        "Student",
    ],
    "count"     : 46,
    "extension" : "webp",
    "gallery_id": "653c2aeaa693c",
    "language"  : "Español",
    "num"       : int,
    "tags"      : [
        "milf",
        "Madre",
        "enormes pechos",
        "Peluda",
        "nakadashi",
        "cheating",
        "madura",
        "sexo a escondidas",
        "Ama de casa",
        "mamada",
    ],
    "title"     : "La Mama de mi Novia es tan Pervertida que no Pude Soportarlo mas",
    "uploader"  : "NekoCreme Fansub",
},

{
    "#url"     : "https://tmohentai.com/reader/653c2aeaa693c/paginated/1",
    "#category": ("", "tmohentai", "gallery"),
    "#class"   : tmohentai.TmohentaiGalleryExtractor,
},

)
