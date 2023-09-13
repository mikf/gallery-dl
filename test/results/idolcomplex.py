# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import idolcomplex


__tests__ = (
{
    "#url"     : "https://idol.sankakucomplex.com/?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
    "#pattern" : r"https://is\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}/[^/]{32}\.\w+\?e=\d+&m=[^&#]+",
    "#range"   : "18-22",
    "#count"   : 5,
},

{
    "#url"     : "https://idol.sankakucomplex.com/?tags=order:favcount",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
    "#range"   : "18-22",
    "#count"   : 5,
},

{
    "#url"     : "https://idol.sankakucomplex.com/?tags=lyumos+wreath&page=3&next=694215",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/pool/show/145",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
    "#count"   : 3,
},

{
    "#url"     : "https://idol.sankakucomplex.com/post/show/694215",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
    "#options"     : {"tags": True},
    "#sha1_content": "694ec2491240787d75bf5d0c75d0082b53a85afd",

    "tags_character": "shani_(the_witcher)",
    "tags_copyright": "the_witcher",
    "tags_idol"     : str,
    "tags_medium"   : str,
    "tags_general"  : str,
},

)
