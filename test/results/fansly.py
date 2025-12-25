# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fansly


__tests__ = (
{
    "#url"     : "https://fansly.com/post/819035448046268416",
    "#comment" : "1 video",
    "#class"   : fansly.FanslyPostExtractor,
},

{
    "#url"     : "https://fansly.com/post/815337432600821760",
    "#comment" : "4 images",
    "#class"   : fansly.FanslyPostExtractor,
},

{
    "#url"     : "https://fansly.com/post/800553913467023361",
    "#comment" : "more than 5 files in an 'accountMediaBundles' entry",
    "#class"   : fansly.FanslyPostExtractor,
    "#auth"    : True,
    "#count"   : 6,
},

{
    "#url"     : "https://fansly.com/post/545313467469410305",
    "#comment" : "'This post does not exist or has been deleted.'",
    "#class"   : fansly.FanslyPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://fansly.com/post/543835794918354944",
    "#comment" : "one locked image",
    "#class"   : fansly.FanslyPostExtractor,
    "#pattern" : r"https://cdn3.fansly.com/364164066794549248/542559086856646656.jpeg\?.+",
    "#count"   : 1,
    "#auth"    : False,
    "#log"     : (
        "No 'token' provided",
        "543835794918354944/542560754868432896: No format available",
    ),
},

{
    "#url"     : "https://fansly.com/post/451349524175138816",
    "#comment" : "locked image + 2 locked videos",
    "#class"   : fansly.FanslyPostExtractor,
    "#count"   : 0,
    "#auth"    : False,
    "#log"     : (
        "No 'token' provided",
        "451349524175138816/451349523013316609: No format available",
        "451349524175138816/451349523000729600: No format available",
        "451349524175138816/451349523025899520: No format available",
    ),
},

{
    "#url"     : "https://fansly.com/post/831751284628414464",
    "#comment" : "video - best format is non-manifest",
    "#class"   : fansly.FanslyPostExtractor,
    "#pattern" : r"https://cdn\d+.fansly.com/788576864472932352/831751193247105025.mp4\?.+",

    "content"        : "off duty miyabi (⸝⸝> ω <⸝⸝)",
    "date"           : "dt:2025-10-07 01:08:38",
    "expiresAt"      : None,
    "extension"      : "mp4",
    "filename"       : "831751193247105025",
    "id"             : "831751284628414464",
    "file"           : {
        "accountId"     : "788576864472932352",
        "createdAt"     : 1759799297,
        "date"          : "dt:2025-10-07 01:08:17",
        "date_updated"  : "dt:2025-10-07 01:08:26",
        "duration"      : 12.376667,
        "flags"         : 6,
        "format"        : 2,
        "frameRate"     : 30.05,
        "height"        : 590,
        "id"            : "831751193247105025",
        "location"      : "/788576864472932352/831751193247105025.mp4",
        "mimetype"      : "video/mp4",
        "originalHeight": 590,
        "originalWidth" : 786,
        "preview"       : False,
        "resolutionMode": 1,
        "status"        : 1,
        "type"          : "video",
        "updatedAt"     : 1759799306,
        "variantHash"   : {},
        "width"         : 786,
    },
},

{
    "#url"     : "https://fansly.com/post/527804734266941440",
    "#comment" : "preview image (#8686)",
    "#class"   : fansly.FanslyPostExtractor,
    "#auth"    : "token",
    "#pattern" : r"https://cdn3.fansly.com/509388488890658816/527804380229935104.jpeg\?ngsw-bypass=true&Expires=\d+.+",

    "createdAt"      : 1687332814,
    "date"           : "dt:2023-06-21 07:33:34",
    "extension"      : "jpeg",
    "filename"       : "527804380229935104",
    "fypFlags"       : 2,
    "id"             : "527804734266941440",
    "file"           : {
        "accountId"     : "509388488890658816",
        "createdAt"     : 1687332730,
        "date"          : "dt:2023-06-21 07:32:10",
        "date_updated"  : "dt:2023-06-21 07:32:13",
        "flags"         : 394,
        "format"        : 1,
        "height"        : 1464,
        "id"            : "527804380229935104",
        "location"      : "/509388488890658816/527804380229935104.jpeg",
        "mimetype"      : "image/jpeg",
        "preview"       : True,
        "resolutionMode": 2,
        "status"        : 1,
        "type"          : "image",
        "updatedAt"     : 1687332733,
        "variantHash"   : {},
        "width"         : 1349,
    },
},

{
    "#url"     : "https://fansly.com/Oliviaus/posts",
    "#class"   : fansly.FanslyCreatorPostsExtractor,
},

{
    "#url"     : "https://fansly.com/Oliviaus/posts/wall/785261459306196992",
    "#class"   : fansly.FanslyCreatorPostsExtractor,
},

{
    "#url"     : "https://fansly.com/Oliviaus/media",
    "#class"   : fansly.FanslyCreatorMediaExtractor,
},

{
    "#url"     : "https://fansly.com/Oliviaus/media/wall/785261459306196992",
    "#class"   : fansly.FanslyCreatorMediaExtractor,
},

{
    "#url"     : "https://fansly.com/VchiBan/media",
    "#comment" : "posts without 'accountId' or 'contentId'",
    "#class"   : fansly.FanslyCreatorMediaExtractor,
},

{
    "#url"     : "https://fansly.com/home",
    "#class"   : fansly.FanslyHomeExtractor,
},

{
    "#url"     : "https://fansly.com/home/subscribed",
    "#class"   : fansly.FanslyHomeExtractor,
},

{
    "#url"     : "https://fansly.com/home/list/1234567890",
    "#class"   : fansly.FanslyHomeExtractor,
},

{
    "#url"     : "https://fansly.com/lists/1234567890",
    "#class"   : fansly.FanslyListExtractor,
},

{
    "#url"     : "https://fansly.com/lists",
    "#class"   : fansly.FanslyListsExtractor,
},

)
