# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imhentai


__tests__ = (
{
    "#url"     : "https://hentaifox.com/gallery/56622/",
    "#category": ("IMHentai", "hentaifox", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,
    "#pattern" : r"https://i\d*\.hentaifox\.com/\d+/\d+/\d+\.jpg",
    "#count"   : 24,

    "count"     : 24,
    "extension" : "jpg",
    "filename"  : str,
    "gallery_id": 56622,
    "width"     : 1143,
    "height"    : 1600,
    "lang"      : "en",
    "num"       : range(1, 24),
    "title"     : "TSF no F no Hon Sono 3 no B - Ch.1",
    "title_alt" : "",
    "type"      : "doujinshi",

    "artist"    : [
        "taniyaraku",
    ],
    "character" : [],
    "group"     : [
        "tsf no f",
    ],
    "language"  : [
        "english",
        "translated",
    ],
    "parody"    : [
        "original",
    ],
    "tags"      : [
        "breast expansion",
        "clothed male nude female",
        "fingering",
        "full censorship",
        "gender bender",
        "glasses",
        "mind break",
        "sole female",
        "sole male",
        "transformation",
    ],
},

{
    "#url"     : "https://hentaifox.com/gallery/630/",
    "#comment" : "'split_tag' element (#1378)",
    "#category": ("IMHentai", "hentaifox", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,

    "artist"    : [
        "beti",
        "betty",
        "magi",
        "mimikaki",
    ],
    "character": [
        "aerith gainsborough",
        "tifa lockhart",
        "yuffie kisaragi",
    ],
    "count"     : 32,
    "gallery_id": 630,
    "group"     : ["cu-little2"],
    "parody"    : [
        "darkstalkers | vampire",
        "final fantasy vii",
    ],
    "tags"      : [
        "femdom",
        "fingering",
        "masturbation",
        "yuri",
    ],
    "title"     : "Cu-Little Bakanyaï½ž",
    "type"      : "doujinshi",
},

{
    "#url"     : "https://hentaifox.com/gallery/35261/",
    "#comment" : "email-protected title (#4201)",
    "#category": ("IMHentai", "hentaifox", "gallery"),
    "#class"   : imhentai.ImhentaiGalleryExtractor,

    "gallery_id": 35261,
    "title"     : "ManageM@ster!",
    "artist"    : ["haritama hiroki"],
    "group"     : ["studio n.ball"],
},

{
    "#url"     : "https://hentaifox.com/parody/touhou-project/",
    "#category": ("IMHentai", "hentaifox", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
},

{
    "#url"     : "https://hentaifox.com/character/reimu-hakurei/",
    "#category": ("IMHentai", "hentaifox", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
},

{
    "#url"     : "https://hentaifox.com/artist/distance/",
    "#category": ("IMHentai", "hentaifox", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
},

{
    "#url"     : "https://hentaifox.com/group/v-slash/",
    "#category": ("IMHentai", "hentaifox", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
},

{
    "#url"     : "https://hentaifox.com/tag/heterochromia/",
    "#category": ("IMHentai", "hentaifox", "tag"),
    "#class"   : imhentai.ImhentaiTagExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(180, 220),
},

{
    "#url"     : "https://hentaifox.com/search/?q=touhou+filming",
    "#category": ("IMHentai", "hentaifox", "search"),
    "#class"   : imhentai.ImhentaiSearchExtractor,
    "#pattern" : imhentai.ImhentaiGalleryExtractor.pattern,
    "#count"   : range(20, 30),
},

{
    "#url"     : "https://hentaifox.com/search/touhou/",
    "#category": ("IMHentai", "hentaifox", "search"),
    "#class"   : imhentai.ImhentaiSearchExtractor,
},

)
