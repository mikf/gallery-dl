# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import sankakucomplex


__tests__ = (
{
    "#url"     : "https://www.sankakucomplex.com/2019/05/11/twitter-cosplayers",
    "#category": ("", "sankakucomplex", "article"),
    "#class"   : sankakucomplex.SankakucomplexArticleExtractor,
    "#sha1_url"     : "4a9ecc5ae917fbce469280da5b6a482510cae84d",
    "#sha1_metadata": "bfe08310e7d9a572f568f6900e0ed0eb295aa2b3",
},

{
    "#url"     : "https://www.sankakucomplex.com/2009/12/01/sexy-goddesses-of-2ch",
    "#category": ("", "sankakucomplex", "article"),
    "#class"   : sankakucomplex.SankakucomplexArticleExtractor,
    "#sha1_url"     : "a1e249173fd6c899a8134fcfbd9c925588a63f7c",
    "#sha1_metadata": "e78fcc23c2711befc0969a45ea5082a29efccf68",
},

{
    "#url"     : "https://www.sankakucomplex.com/2019/06/11/darling-ol-goddess-shows-off-her-plump-lower-area/",
    "#comment" : "videos (#308)",
    "#category": ("", "sankakucomplex", "article"),
    "#class"   : sankakucomplex.SankakucomplexArticleExtractor,
    "#pattern" : r"/wp-content/uploads/2019/06/[^/]+\d\.mp4",
    "#range"   : "26-",
    "#count"   : 5,
},

{
    "#url"     : "https://www.sankakucomplex.com/2015/02/12/snow-miku-2015-live-magical-indeed/",
    "#comment" : "youtube embeds (#308)",
    "#category": ("", "sankakucomplex", "article"),
    "#class"   : sankakucomplex.SankakucomplexArticleExtractor,
    "#options" : {"embeds": True},
    "#pattern" : "https://www.youtube.com/embed/",
    "#range"   : "2-",
    "#count"   : 2,
},

{
    "#url"     : "https://www.sankakucomplex.com/tag/cosplay/",
    "#category": ("", "sankakucomplex", "tag"),
    "#class"   : sankakucomplex.SankakucomplexTagExtractor,
    "#pattern" : sankakucomplex.SankakucomplexArticleExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://www.sankakucomplex.com/category/anime/",
    "#category": ("", "sankakucomplex", "tag"),
    "#class"   : sankakucomplex.SankakucomplexTagExtractor,
},

{
    "#url"     : "https://www.sankakucomplex.com/author/rift/page/5/",
    "#category": ("", "sankakucomplex", "tag"),
    "#class"   : sankakucomplex.SankakucomplexTagExtractor,
},

)
