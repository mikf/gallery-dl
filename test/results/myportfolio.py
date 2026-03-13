# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import myportfolio
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://andrewling.myportfolio.com/volvo-xc-90-hybrid",
    "#class"   : myportfolio.MyportfolioGalleryExtractor,
    "#sha1_url"     : "acea0690c76db0e5cf267648cefd86e921bc3499",
    "#sha1_metadata": "6ac6befe2ee0af921d24cf1dd4a4ed71be06db6d",
},

{
    "#url"     : "https://andrewling.myportfolio.com/",
    "#class"   : myportfolio.MyportfolioGalleryExtractor,
    "#pattern" : r"https://andrewling\.myportfolio\.com/[^/?#+]+$",
    "#count"   : ">= 6",
},

{
    "#url"     : "https://stevenilousphotography.myportfolio.com/society",
    "#class"   : myportfolio.MyportfolioGalleryExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "myportfolio:https://tooco.com.ar/6-of-diamonds-paradise-bird",
    "#comment" : "custom domain",
    "#class"   : myportfolio.MyportfolioGalleryExtractor,
    "#count"   : 3,
},

{
    "#url"     : "myportfolio:https://tooco.com.ar/",
    "#class"   : myportfolio.MyportfolioGalleryExtractor,
    "#pattern" : myportfolio.MyportfolioGalleryExtractor.pattern,
    "#count"   : ">= 40",
},

{
    "#url"     : "https://cdn.myportfolio.com/f33febb6-e0cb-4216-872f-b5b39bb2d451/74676fd6-d7e2-40ac-928f-9ea6f90a43b8.jpg?h=d3e8429d039657df820622c5e4d6c7ab",
    "#comment" : "disallow 'cdn' subdomain",
    "#class"   : myportfolio.MyportfolioGalleryExtractor,
    "#fail"    : True,
},

)
