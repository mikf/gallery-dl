# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nhentai


__tests__ = (
{
    "#url"     : "https://nhentai.net/g/147850/",
    "#category": ("", "nhentai", "gallery"),
    "#class"   : nhentai.NhentaiGalleryExtractor,
    "#sha1_url": "5179dbf0f96af44005a0ff705a0ad64ac26547d0",

    "title"     : r"re:\[Morris\] Amazon no Hiyaku \| Amazon Elixir",
    "title_en"  : str,
    "title_ja"  : str,
    "gallery_id": 147850,
    "media_id"  : 867789,
    "count"     : 16,
    "date"      : 1446050915,
    "scanlator" : "",
    "artist"    : ["morris"],
    "group"     : list,
    "parody"    : list,
    "characters": list,
    "tags"      : list,
    "type"      : "manga",
    "lang"      : "en",
    "language"  : "English",
    "width"     : int,
    "height"    : int,
},

{
    "#url"     : "https://nhentai.net/tag/sole-female/",
    "#category": ("", "nhentai", "tag"),
    "#class"   : nhentai.NhentaiTagExtractor,
    "#pattern" : nhentai.NhentaiGalleryExtractor.pattern,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://nhentai.net/artist/itou-life/",
    "#category": ("", "nhentai", "tag"),
    "#class"   : nhentai.NhentaiTagExtractor,
},

{
    "#url"     : "https://nhentai.net/group/itou-life/",
    "#category": ("", "nhentai", "tag"),
    "#class"   : nhentai.NhentaiTagExtractor,
},

{
    "#url"     : "https://nhentai.net/parody/touhou-project/",
    "#category": ("", "nhentai", "tag"),
    "#class"   : nhentai.NhentaiTagExtractor,
},

{
    "#url"     : "https://nhentai.net/character/patchouli-knowledge/popular",
    "#category": ("", "nhentai", "tag"),
    "#class"   : nhentai.NhentaiTagExtractor,
},

{
    "#url"     : "https://nhentai.net/category/doujinshi/popular-today",
    "#category": ("", "nhentai", "tag"),
    "#class"   : nhentai.NhentaiTagExtractor,
},

{
    "#url"     : "https://nhentai.net/language/english/popular-week",
    "#category": ("", "nhentai", "tag"),
    "#class"   : nhentai.NhentaiTagExtractor,
},

{
    "#url"     : "https://nhentai.net/search/?q=touhou",
    "#category": ("", "nhentai", "search"),
    "#class"   : nhentai.NhentaiSearchExtractor,
    "#pattern" : nhentai.NhentaiGalleryExtractor.pattern,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://nhentai.net/favorites/",
    "#category": ("", "nhentai", "favorite"),
    "#class"   : nhentai.NhentaiFavoriteExtractor,
},

)
