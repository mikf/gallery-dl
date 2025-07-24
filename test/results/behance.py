# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import behance
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.behance.net/gallery/17386197/A-Short-Story",
    "#class"   : behance.BehanceGalleryExtractor,
    "#results" : (
        "ytdl:https://player.vimeo.com/video/97189640?title=0&byline=0&portrait=0&color=ffffff",
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/a5a12417386197.562bc055a107d.jpg",
    ),

    "id"    : 17386197,
    "date"  : "dt:2014-06-03 15:41:51",
    "name"  : r"re:\"Hi\". A short story about the important things ",
    "module": dict,

    "owners": [
        "Place Studio",
        "Julio César Velazquez",
    ],
    "creator": {
        "displayName"     : "Place Studio",
        "hasAllowEmbeds"  : True,
        "hasPremiumAccess": False,
        "id"              : 119690,
        "name"            : "weareplace",
        "url"             : "https://www.behance.net/weareplace",
    },
    "?fields": [
        "Animation",
        "Character Design",
        "Directing",
    ],
    "tags": [
        "short",
        "life",
        "motion",
        "hi",
        "toon",
        "kids",
        "Character",
        "story",
        "happy",
        "shape",
        "disney",
    ],
},

{
    "#url"     : "https://www.behance.net/gallery/21324767/Nevada-City",
    "#class"   : behance.BehanceGalleryExtractor,
    "#results" : (
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/f5230a21324767.562ff473c2945.jpg",
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/5674c921324767.562ff473a3ef8.jpg",
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/9f6d3b21324767.562ff473c9da5.jpg",
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/3781c921324767.562ff473afa1c.jpg",
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/02011a21324767.562ff473bed3d.jpg",
        "https://mir-s3-cdn-cf.behance.net/project_modules/source/2a65cf21324767.562ff473b7e3d.jpg",
    ),

    "creator": {"name": "alexstrohl"},
    "owners" : ["Alex Strohl"],
},

{
    "#url"     : "https://www.behance.net/gallery/88276087/Audi-R8-RWD",
    "#comment" : "'media_collection' modules",
    "#class"   : behance.BehanceGalleryExtractor,
    "#pattern" : r"https://mir-s3-cdn-cf\.behance\.net/project_modules/source/[0-9a-f]+.[0-9a-f]+\.jpg",
    "#count"   : 20,
    "#sha1_url": "6bebff0d37f85349f9ad28bd8b76fd66627c1e2f",

    "creator": {"name": "AgnieszkaDoroszewicz"},
    "owners" : ["Agnieszka Doroszewicz"],
},

{
    "#url"     : "https://www.behance.net/gallery/101185577/COLCCI",
    "#comment" : "'video' modules (#1282)",
    "#class"   : behance.BehanceGalleryExtractor,
    "#pattern" : r"ytdl:https://cdn-prod-ccv\.adobe\.com/\w+/rend/master\.m3u8\?",
    "#count"   : 3,

    "creator": {"name": "brnsimao"},
    "owners" : ["Bruno Simao"],
},

{
    "#url"     : "https://www.behance.net/gallery/89270715/Moevir",
    "#comment" : "'text' modules (#4799)",
    "#class"   : behance.BehanceGalleryExtractor,
    "#options" : {"modules": "text"},
    "#results" : """text:<div>Make Shift<br><a href="https://www.moevir.com/News/make-shif?fbclid=IwAR2MXL7mVDskdXHitLs4tv_RQFqB1tpAYix2EMIzea4lOSIPdPOR45wEJMA" target="_blank" rel="nofollow">https://www.moevir.com/News/make-shif</a><br>Moevir Magazine November Issue 2019<br>Photography by Caesar Lima @caephoto <br>Model: Bee @phamhuongbee <br>Makeup by Monica Alvarez @monicaalvarezmakeup <br>Styling by Jessica Boal @jessicaboal <br>Hair by James Gilbert @brandnewjames<br>Shot at Vila Sophia<br></div>""",

    "creator": {"name": "caephoto"},
    "owners" : ["Caesar Lima"],
},

{
    "#url"     : "https://www.behance.net/gallery/177464639/Kimori",
    "#comment" : "mature content (#4417)",
    "#class"   : behance.BehanceGalleryExtractor,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://www.behance.net/alexstrohl",
    "#class"   : behance.BehanceUserExtractor,
    "#pattern" : behance.BehanceGalleryExtractor.pattern,
    "#count"   : ">= 11",
},

{
    "#url"     : "https://www.behance.net/collection/71340149/inspiration",
    "#class"   : behance.BehanceCollectionExtractor,
    "#pattern" : behance.BehanceGalleryExtractor.pattern,
    "#count"   : ">= 150",

    "!creator": dict,
},

)
