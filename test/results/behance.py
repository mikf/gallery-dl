# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import behance
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.behance.net/gallery/17386197/A-Short-Story",
    "#category": ("", "behance", "gallery"),
    "#class"   : behance.BehanceGalleryExtractor,
    "#urls"    : (
        "ytdl:https://player.vimeo.com/video/97189640?title=0&byline=0&portrait=0&color=ffffff",
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/a5a12417386197.562bc055a107d.jpg",
    ),

    "id"    : 17386197,
    "name"  : r"re:\"Hi\". A short story about the important things ",
    "owners": [
        "Place Studio",
        "Julio César Velazquez",
    ],
    "?fields": [
        "Animation",
        "Character Design",
        "Directing",
    ],
    "tags"  : list,
    "module": dict,
    "date"  : "dt:2014-06-03 15:41:51",
},

{
    "#url"     : "https://www.behance.net/gallery/21324767/Nevada-City",
    "#category": ("", "behance", "gallery"),
    "#class"   : behance.BehanceGalleryExtractor,
    "#count"   : 6,
    "#sha1_url": "0258fe194fe7d828d6f2c7f6086a9a0a4140db1d",

    "owners": ["Alex Strohl"],
},

{
    "#url"     : "https://www.behance.net/gallery/88276087/Audi-R8-RWD",
    "#comment" : "'media_collection' modules",
    "#category": ("", "behance", "gallery"),
    "#class"   : behance.BehanceGalleryExtractor,
    "#pattern" : r"https://mir-s3-cdn-cf\.behance\.net/project_modules/source/[0-9a-f]+.[0-9a-f]+\.jpg",
    "#count"   : 20,
    "#sha1_url": "6bebff0d37f85349f9ad28bd8b76fd66627c1e2f",
},

{
    "#url"     : "https://www.behance.net/gallery/101185577/COLCCI",
    "#comment" : "'video' modules (#1282)",
    "#category": ("", "behance", "gallery"),
    "#class"   : behance.BehanceGalleryExtractor,
    "#pattern" : r"ytdl:https://cdn-prod-ccv\.adobe\.com/\w+/rend/master\.m3u8\?",
    "#count"   : 3,
},

{
    "#url"     : "https://www.behance.net/gallery/89270715/Moevir",
    "#comment" : "'text' modules (#4799)",
    "#category": ("", "behance", "gallery"),
    "#class"   : behance.BehanceGalleryExtractor,
    "#options" : {"modules": "text"},
    "#urls"    : """text:<div>Make Shift<br><a href="https://www.moevir.com/News/make-shif?fbclid=IwAR2MXL7mVDskdXHitLs4tv_RQFqB1tpAYix2EMIzea4lOSIPdPOR45wEJMA" target="_blank" rel="nofollow">https://www.moevir.com/News/make-shif</a><br>Moevir Magazine November Issue 2019<br>Photography by Caesar Lima @caephoto <br>Model: Bee @phamhuongbee <br>Makeup by Monica Alvarez @monicaalvarezmakeup <br>Styling by Jessica Boal @jessicaboal <br>Hair by James Gilbert @brandnewjames<br>Shot at Vila Sophia<br></div>""",
},

{
    "#url"     : "https://www.behance.net/gallery/177464639/Kimori",
    "#comment" : "mature content (#4417)",
    "#category": ("", "behance", "gallery"),
    "#class"   : behance.BehanceGalleryExtractor,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://www.behance.net/alexstrohl",
    "#category": ("", "behance", "user"),
    "#class"   : behance.BehanceUserExtractor,
    "#pattern" : behance.BehanceGalleryExtractor.pattern,
    "#count"   : ">= 11",
},

{
    "#url"     : "https://www.behance.net/collection/71340149/inspiration",
    "#category": ("", "behance", "collection"),
    "#class"   : behance.BehanceCollectionExtractor,
    "#pattern" : behance.BehanceGalleryExtractor.pattern,
    "#count"   : ">= 150",
},

)
