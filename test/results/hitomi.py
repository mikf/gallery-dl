# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hitomi
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://hitomi.la/galleries/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#pattern"      : r"https://[a-c]a\.hitomi\.la/webp/\d+/\d+/[0-9a-f]{64}\.webp",
    "#count"        : 16,
    "#sha1_metadata": "86af5371f38117a07407f11af689bdd460b09710",
},

{
    "#url"     : "https://hitomi.la/galleries/1401410.html",
    "#comment" : "download test",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#range"       : "1",
    "#sha1_content": "d75d5a3d1302a48469016b20e53c26b714d17745",
},

{
    "#url"     : "https://hitomi.la/galleries/733697.html",
    "#comment" : "Game CG with scenes (#321)",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#count"   : 210,
},

{
    "#url"     : "https://hitomi.la/galleries/1045954.html",
    "#comment" : "fallback for galleries only available through /reader/ URLs",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#count"   : 1413,
},

{
    "#url"     : "https://hitomi.la/cg/scathacha-sama-okuchi-ecchi-1291900.html",
    "#comment" : "gallery with 'broken' redirect",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://hitomi.la/cg/1615823.html",
    "#comment" : "no tags",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
    "#options" : {"format": "avif"},
    "#pattern" : r"https://[a-c]a\.hitomi\.la/avif/\d+/\d+/[0-9a-f]{64}\.avif",
    "#count"   : 22,
},

{
    "#url"     : "https://hitomi.la/manga/amazon-no-hiyaku-867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/manga/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/doujinshi/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/cg/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/gamecg/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/imageset/867789.html",
    "#comment" : "/imageset/ gallery (#4756)",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/reader/867789.html",
    "#category": ("", "hitomi", "gallery"),
    "#class"   : hitomi.HitomiGalleryExtractor,
},

{
    "#url"     : "https://hitomi.la/tag/screenshots-japanese.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
    "#pattern" : hitomi.HitomiGalleryExtractor.pattern,
    "#count"   : ">= 35",
},

{
    "#url"     : "https://hitomi.la/artist/a1-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/group/initial%2Dg-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/series/amnesia-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/type/doujinshi-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

{
    "#url"     : "https://hitomi.la/character/a2-all-1.html",
    "#category": ("", "hitomi", "tag"),
    "#class"   : hitomi.HitomiTagExtractor,
},

)
