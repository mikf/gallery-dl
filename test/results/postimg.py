# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://postimages.org/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
},

{
    "#url"     : "https://www.postimages.org/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
},

{
    "#url"     : "https://pixxxels.cc/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
},

{
    "#url"     : "https://postimg.cc/Wtn2b3hC",
    "#category": ("imagehost", "postimg", "image"),
    "#class"   : imagehosts.PostimgImageExtractor,
    "#sha1_url"     : "72f3c8b1d6c6601a20ad58f35635494b4891a99e",
    "#sha1_metadata": "2d05808d04e4e83e33200db83521af06e3147a84",
    "#sha1_content" : "cfaa8def53ed1a575e0c665c9d6d8cf2aac7a0ee",
},

{
    "#url"     : "https://postimg.cc/gallery/wxpDLgX",
    "#category": ("imagehost", "postimg", "gallery"),
    "#class"   : imagehosts.PostimgGalleryExtractor,
    "#pattern" : imagehosts.PostimgImageExtractor.pattern,
    "#count"   : 22,
},

)
