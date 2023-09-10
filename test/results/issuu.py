# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import issuu


__tests__ = (
{
    "#url"     : "https://issuu.com/issuu/docs/motions-1-2019/",
    "#category": ("", "issuu", "publication"),
    "#class"   : issuu.IssuuPublicationExtractor,
    "#pattern" : r"https://image.isu.pub/190916155301-\w+/jpg/page_\d+.jpg",
    "#count"   : 36,

    "document" : {
        "access"       : "PUBLIC",
        "contentRating": {
            "isAdsafe"  : True,
            "isExplicit": False,
            "isReviewed": True,
        },
        "date"         : "dt:2019-09-16 00:00:00",
        "description"  : r"re:Motions, the brand new publication by I",
        "documentName" : "motions-1-2019",
        "downloadable" : False,
        "pageCount"    : 36,
        "publicationId": "d99ec95935f15091b040cb8060f05510",
        "title"        : "Motions by Issuu - Issue 1",
        "username"     : "issuu",
    },
    "extension": "jpg",
    "filename" : r"re:page_\d+",
    "num"      : int,
},

{
    "#url"     : "https://issuu.com/issuu",
    "#category": ("", "issuu", "user"),
    "#class"   : issuu.IssuuUserExtractor,
    "#pattern" : issuu.IssuuPublicationExtractor.pattern,
    "#count"   : "> 25",
},

)
