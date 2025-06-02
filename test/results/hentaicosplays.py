# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentaicosplays


__tests__ = (
{
    "#url"     : "https://hentai-cosplay-xxx.com/image/---devilism--tide-kurihara-/",
    "#category": ("hentaicosplays", "hentaicosplay", "gallery"),
    "#class"   : hentaicosplays.HentaicosplaysGalleryExtractor,
    "#pattern" : r"https://static\d?\.hentai-cosplay-xxx\.com/upload/\d+/\d+/\d+/\d+\.jpg$",

    "count": 18,
    "site" : "hentai-cosplay-xxx",
    "slug" : "---devilism--tide-kurihara-",
    "title": "艦 こ れ-devilism の tide Kurihara 憂",
},

{
    "#url"     : "https://hentai-cosplays.com/image/---devilism--tide-kurihara-/",
    "#category": ("hentaicosplays", "hentaicosplay", "gallery"),
    "#class"   : hentaicosplays.HentaicosplaysGalleryExtractor,
    "#pattern" : r"https://static\d?\.hentai-cosplay-xxx\.com/upload/\d+/\d+/\d+/\d+\.jpg$",

    "count": 18,
    "site" : "hentai-cosplay-xxx",
    "slug" : "---devilism--tide-kurihara-",
    "title": "艦 こ れ-devilism の tide Kurihara 憂",
},

{
    "#url"     : "https://fr.porn-image.com/image/enako-enako-24/",
    "#category": ("hentaicosplays", "pornimage", "gallery"),
    "#class"   : hentaicosplays.HentaicosplaysGalleryExtractor,
    "#pattern" : r"https://static\d?.porn-image.com/upload/\d+/\d+/\d+/\d+.jpg$",

    "count": 11,
    "site" : "porn-image",
    "title": str,
},

{
    "#url"     : "https://fr.porn-images-xxx.com/image/enako-enako-24/",
    "#category": ("hentaicosplays", "pornimage", "gallery"),
    "#class"   : hentaicosplays.HentaicosplaysGalleryExtractor,
},

{
    "#url"     : "https://ja.hentai-img-xxx.com/image/hollow-cora-502/",
    "#category": ("hentaicosplays", "hentaiimg", "gallery"),
    "#class"   : hentaicosplays.HentaicosplaysGalleryExtractor,
    "#pattern" : r"https://static\d?.hentai-img-xxx.com/upload/\d+/\d+/\d+/\d+.jpg$",

    "count": 2,
    "site" : "hentai-img-xxx",
    "title": str,
},

{
    "#url"     : "https://ja.hentai-img.com/image/hollow-cora-502/",
    "#category": ("hentaicosplays", "hentaiimg", "gallery"),
    "#class"   : hentaicosplays.HentaicosplaysGalleryExtractor,
},

)
