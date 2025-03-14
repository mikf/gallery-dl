# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import issuu


__tests__ = (
{
    "#url"     : "https://issuu.com/issuu/docs/motions-1-2019/",
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
    "#url"     : "https://issuu.com/foodhome1955/docs/fh_winter2025-issuu-011625",
    "#comment" : "HTML escapes",
    "#class"   : issuu.IssuuPublicationExtractor,
    "#count"   : 84,

    "document": {
        "access"          : "PUBLIC",
        "date"            : "dt:2025-01-17 00:00:00",
        "description"     : "Santa Barbara's Lifestyle Magazine",
        "documentName"    : "fh_winter2025-issuu-011625",
        "isDocumentGated" : False,
        "originalPublishDateInISOString": "2025-01-17T00:00:00.000Z",
        "pageCount"       : 84,
        "publicationId"   : "b89e35d4bd2201c7ecd871160fe000fa",
        "revisionId"      : "250117005419",
        "title"           : "Food & Home Winter 2025",
        "username"        : "foodhome1955",
        "contentRating"   : {
            "isAdsafe"    : True,
            "isExplicit"  : False,
            "isReviewed"  : True,
        },
        "path"            : {
            "documentName": "fh_winter2025-issuu-011625",
            "type"        : "user",
            "username"    : "foodhome1955",
        },
    },
},

{
    "#url"     : "https://issuu.com/issuu",
    "#class"   : issuu.IssuuUserExtractor,
    "#pattern" : issuu.IssuuPublicationExtractor.pattern,
    "#count"   : range(100, 150),
},

{
    "#url"     : "https://issuu.com/issuu/3",
    "#class"   : issuu.IssuuUserExtractor,
    "#count"   : range(4, 40),
},

)
