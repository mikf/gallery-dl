# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentaihand


__tests__ = (
{
    "#url"     : "https://hentaihand.com/en/comic/c75-takumi-na-muchi-choudenji-hou-no-aishi-kata-how-to-love-a-super-electromagnetic-gun-toaru-kagaku-no-railgun-english",
    "#category": ("", "hentaihand", "gallery"),
    "#class"   : hentaihand.HentaihandGalleryExtractor,
    "#pattern" : r"https://cdn.hentaihand.com/.*/images/37387/\d+.jpg$",
    "#count"   : 50,

    "artists"      : ["Takumi Na Muchi"],
    "date"         : "dt:2014-06-28 00:00:00",
    "gallery_id"   : 37387,
    "lang"         : "en",
    "language"     : "English",
    "parodies"     : ["Toaru Kagaku No Railgun"],
    "relationships": list,
    "tags"         : list,
    "title"        : r"re:\(C75\) \[Takumi na Muchi\] Choudenji Hou ",
    "title_alt"    : r"re:\(C75\) \[たくみなむち\] 超電磁砲のあいしかた",
    "type"         : "Doujinshi",
},

{
    "#url"     : "https://hentaihand.com/en/artist/takumi-na-muchi",
    "#category": ("", "hentaihand", "tag"),
    "#class"   : hentaihand.HentaihandTagExtractor,
    "#pattern" : hentaihand.HentaihandGalleryExtractor.pattern,
    "#count"   : ">= 6",
},

{
    "#url"     : "https://hentaihand.com/en/tag/full-color",
    "#category": ("", "hentaihand", "tag"),
    "#class"   : hentaihand.HentaihandTagExtractor,
},

{
    "#url"     : "https://hentaihand.com/fr/language/japanese",
    "#category": ("", "hentaihand", "tag"),
    "#class"   : hentaihand.HentaihandTagExtractor,
},

{
    "#url"     : "https://hentaihand.com/zh/category/manga",
    "#category": ("", "hentaihand", "tag"),
    "#class"   : hentaihand.HentaihandTagExtractor,
},

)
