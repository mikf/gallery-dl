# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import adultempire


__tests__ = (
{
    "#url"     : "https://www.adultempire.com/5998/gallery.html",
    "#category": ("", "adultempire", "gallery"),
    "#class"   : adultempire.AdultempireGalleryExtractor,
    "#range"        : "1",
    "#sha1_metadata": "5b3266e69801db0d78c22181da23bc102886e027",
    "#sha1_content" : "5c6beb31e5e3cdc90ee5910d5c30f9aaec977b9e",
},

{
    "#url"     : "https://www.adultdvdempire.com/5683/gallery.html",
    "#category": ("", "adultempire", "gallery"),
    "#class"   : adultempire.AdultempireGalleryExtractor,
    "#sha1_url"     : "b12cd1a65cae8019d837505adb4d6a2c1ed4d70d",
    "#sha1_metadata": "8d448d79c4ac5f5b10a3019d5b5129ddb43655e5",
},

)
