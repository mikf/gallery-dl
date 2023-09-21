# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolfuuka


__tests__ = (
{
    "#url"     : "https://archiveofsins.com/h/thread/4668813/",
    "#category": ("foolfuuka", "archiveofsins", "thread"),
    "#class"   : foolfuuka.FoolfuukaThreadExtractor,
    "#sha1_url"    : "f612d287087e10a228ef69517cf811539db9a102",
    "#sha1_content": "0dd92d0d8a7bf6e2f7d1f5ac8954c1bcf18c22a4",
},

{
    "#url"     : "https://archiveofsins.com/h/",
    "#category": ("foolfuuka", "archiveofsins", "board"),
    "#class"   : foolfuuka.FoolfuukaBoardExtractor,
},

{
    "#url"     : "https://archiveofsins.com/_/search/text/test/",
    "#category": ("foolfuuka", "archiveofsins", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://archiveofsins.com/_/search/text/test/",
    "#category": ("foolfuuka", "archiveofsins", "search"),
    "#class"   : foolfuuka.FoolfuukaSearchExtractor,
},

{
    "#url"     : "https://archiveofsins.com/h/gallery/3",
    "#category": ("foolfuuka", "archiveofsins", "gallery"),
    "#class"   : foolfuuka.FoolfuukaGalleryExtractor,
},

)
