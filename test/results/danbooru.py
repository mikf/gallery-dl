# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import danbooru


__tests__ = (
{
    "#url"     : "https://danbooru.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#sha1_content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
},

{
    "#url"     : "https://danbooru.donmai.us/posts?tags=mushishi",
    "#comment" : "test page transitions",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#count"   : ">= 300",
},

{
    "#url"     : "https://danbooru.donmai.us/posts?tags=pixiv_id%3A1476533",
    "#comment" : "'external' option (#1747)",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#options" : {"external": True},
    "#pattern" : r"https://i\.pximg\.net/img-original/img/2008/08/28/02/35/48/1476533_p0\.jpg",
},

{
    "#url"     : "https://hijiribe.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://sonohara.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://safebooru.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://donmai.moe/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/pools/7659",
    "#category": ("Danbooru", "danbooru", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
    "#sha1_content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
},

{
    "#url"     : "https://danbooru.donmai.us/pool/show/7659",
    "#category": ("Danbooru", "danbooru", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/posts/294929",
    "#category": ("Danbooru", "danbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#sha1_content": "5e255713cbf0a8e0801dc423563c34d896bb9229",

    "date": "dt:2008-08-12 04:46:05",
},

{
    "#url"     : "https://danbooru.donmai.us/posts/3613024",
    "#category": ("Danbooru", "danbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#options" : {"ugoira": True},
    "#pattern" : r"https?://.+\.zip$",
},

{
    "#url"     : "https://danbooru.donmai.us/post/show/294929",
    "#category": ("Danbooru", "danbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/explore/posts/popular",
    "#category": ("Danbooru", "danbooru", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/explore/posts/popular?date=2013-06-06&scale=week",
    "#category": ("Danbooru", "danbooru", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
    "#range"   : "1-120",
    "#count"   : 120,
},

)
