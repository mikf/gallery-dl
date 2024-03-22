# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import idolcomplex


__tests__ = (
{
    "#url"     : "https://idol.sankakucomplex.com/en/posts?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
    "#pattern" : r"https://i[sv]\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}/[^/]{32}\.\w+\?e=\d+&m=[^&#]+",
    "#range"   : "18-22",
    "#count"   : 5,
},

{
    "#url"     : "https://idol.sankakucomplex.com/posts/?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/?tags=lyumos+wreath&page=3&next=694215",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/pools/e9PMwnwRBK3",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/pools/show/145",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/pool/show/145",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/posts/vkr36qdOaZ4",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
    "#sha1_content": "694ec2491240787d75bf5d0c75d0082b53a85afd",

    "created_at"    : "2017-11-24 17:01:27.696",
    "date"          : "dt:2017-11-24 17:01:27",
    "extension"     : "jpg",
    "file_url"      : r"re:https://i[sv]\.sankakucomplex\.com/data/50/9e/509eccbba54a43cea6b275a65b93c51d\.jpg\?",
    "filename"      : "509eccbba54a43cea6b275a65b93c51d",
    "height"        : 683,
    "id"            : "vkr36qdOaZ4",  # legacy ID: 694215
    "md5"           : "509eccbba54a43cea6b275a65b93c51d",
    "rating"        : "g",
    "tags"          : "lyumos the_witcher shani_(the_witcher) 1girl green_eyes non-asian redhead waistcoat wreath cosplay 3:2_aspect_ratio",
    "tags_character": "shani_(the_witcher)",
    "tags_copyright": "the_witcher",
    "tags_general"  : "1girl green_eyes non-asian redhead waistcoat wreath",
    "tags_genre"    : "cosplay",
    "tags_idol"     : "lyumos",
    "tags_medium"   : "3:2_aspect_ratio",
    "vote_average"  : range(4, 5),
    "vote_count"    : range(25, 40),
    "width"         : 1024,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/posts/509eccbba54a43cea6b275a65b93c51d",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/posts/show/509eccbba54a43cea6b275a65b93c51d",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/posts/509eccbba54a43cea6b275a65b93c51d",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/post/show/694215",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
    "#sha1_content": "694ec2491240787d75bf5d0c75d0082b53a85afd",

    "id"            : "vkr36qdOaZ4",  # legacy ID: 694215
    "tags_character": "shani_(the_witcher)",
    "tags_copyright": "the_witcher",
    "tags_idol"     : str,
    "tags_medium"   : str,
    "tags_general"  : str,
},

)
