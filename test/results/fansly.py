# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fansly


__tests__ = (
{
    "#url"     : "https://fansly.com/post/819035448046268416",
    "#comment" : "video",
    "#class"   : fansly.FanslyPostExtractor,
},

{
    "#url"     : "https://fansly.com/post/815337432600821760",
    "#comment" : "images",
    "#class"   : fansly.FanslyPostExtractor,
},

{
    "#url"     : "https://fansly.com/Oliviaus/posts",
    "#class"   : fansly.FanslyCreatorPostsExtractor,
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

)
