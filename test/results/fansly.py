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
