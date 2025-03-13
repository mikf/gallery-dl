# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://www.turboimagehost.com/p/39078423/test--.png.html",
    "#category": ("imagehost", "turboimagehost", "image"),
    "#class"   : imagehosts.TurboimagehostImageExtractor,
    "#sha1_url"     : "b94de43612318771ced924cb5085976f13b3b90e",
    "#sha1_metadata": "704757ca8825f51cec516ec44c1e627c1f2058ca",
    "#sha1_content" : (
        "f38b54b17cd7462e687b58d83f00fca88b1b105a",
        "0c8768055e4e20e7c7259608b67799171b691140",
        "961b25d85b5f5bd18cbe3e847ac55925f14d0286"
    ),
},

{
    "#url"     : "https://www.turboimagehost.com/album/344597/testimagegallery",
    "#category": ("imagehost", "turboimagehost", "gallery"),
    "#class"   : imagehosts.TurboimagehostGalleryExtractor,
    "#pattern" : imagehosts.TurboimagehostImageExtractor.pattern,
    "#sha1_url": "f2d4fe102fdd71dd1f595cdb0c16ce999d6bb19b",
    "#count"   : 110,
},

)
