# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://www.imagevenue.com/ME13LS07",
    "#category": ("imagehost", "imagevenue", "image"),
    "#class"   : imagehosts.ImagevenueImageExtractor,
    "#pattern"      : r"https://cdn-images\.imagevenue\.com/10/ac/05/ME13LS07_o\.png",
    "#sha1_metadata": "ae15d6e3b2095f019eee84cd896700cd34b09c36",
    "#sha1_content" : "cfaa8def53ed1a575e0c665c9d6d8cf2aac7a0ee",
},

{
    "#url"     : "https://www.imagevenue.com/view/o?i=92518_13732377annakarina424200712535AM_122_486lo.jpg&h=img150&l=loc486",
    "#category": ("imagehost", "imagevenue", "image"),
    "#class"   : imagehosts.ImagevenueImageExtractor,
    "#sha1_url": "8bf0254e29250d8f5026c0105bbdda3ee3d84980",
},

{
    "#url"     : "http://img28116.imagevenue.com/img.php?image=th_52709_test_122_64lo.jpg",
    "#category": ("imagehost", "imagevenue", "image"),
    "#class"   : imagehosts.ImagevenueImageExtractor,
    "#sha1_url": "f98e3091df7f48a05fb60fbd86f789fc5ec56331",
},

)
