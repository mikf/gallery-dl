# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentaifox


__tests__ = (
{
    "#url"     : "https://hentaifox.com/gallery/56622/",
    "#category": ("", "hentaifox", "gallery"),
    "#class"   : hentaifox.HentaifoxGalleryExtractor,
    "#pattern"      : r"https://i\d*\.hentaifox\.com/\d+/\d+/\d+\.jpg",
    "#count"        : 24,
    "#sha1_metadata": "bcd6b67284f378e5cc30b89b761140e3e60fcd92",
},

{
    "#url"     : "https://hentaifox.com/gallery/630/",
    "#comment" : "'split_tag' element (#1378)",
    "#category": ("", "hentaifox", "gallery"),
    "#class"   : hentaifox.HentaifoxGalleryExtractor,

    "artist"    : [
        "beti",
        "betty",
        "magi",
        "mimikaki",
    ],
    "characters": [
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
    "#category": ("", "hentaifox", "gallery"),
    "#class"   : hentaifox.HentaifoxGalleryExtractor,

    "gallery_id": 35261,
    "title"     : "ManageM@ster!",
    "artist"    : ["haritama hiroki"],
    "group"     : ["studio n.ball"],
},

{
    "#url"     : "https://hentaifox.com/parody/touhou-project/",
    "#category": ("", "hentaifox", "search"),
    "#class"   : hentaifox.HentaifoxSearchExtractor,
},

{
    "#url"     : "https://hentaifox.com/character/reimu-hakurei/",
    "#category": ("", "hentaifox", "search"),
    "#class"   : hentaifox.HentaifoxSearchExtractor,
},

{
    "#url"     : "https://hentaifox.com/artist/distance/",
    "#category": ("", "hentaifox", "search"),
    "#class"   : hentaifox.HentaifoxSearchExtractor,
},

{
    "#url"     : "https://hentaifox.com/search/touhou/",
    "#category": ("", "hentaifox", "search"),
    "#class"   : hentaifox.HentaifoxSearchExtractor,
},

{
    "#url"     : "https://hentaifox.com/group/v-slash/",
    "#category": ("", "hentaifox", "search"),
    "#class"   : hentaifox.HentaifoxSearchExtractor,
},

{
    "#url"     : "https://hentaifox.com/tag/heterochromia/",
    "#category": ("", "hentaifox", "search"),
    "#class"   : hentaifox.HentaifoxSearchExtractor,
    "#pattern" : hentaifox.HentaifoxGalleryExtractor.pattern,
    "#count"   : ">= 60",

    "url"       : str,
    "gallery_id": int,
    "title"     : str,
},

)
