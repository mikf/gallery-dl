# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://pixhost.to/show/190/130327671_test-.png",
    "#category": ("imagehost", "pixhost", "image"),
    "#class"   : imagehosts.PixhostImageExtractor,
    "#sha1_url"     : "4e5470dcf6513944773044d40d883221bbc46cff",
    "#sha1_metadata": "3bad6d59db42a5ebbd7842c2307e1c3ebd35e6b0",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",
},

{
    "#url"     : "https://pixhost.to/gallery/jSMFq",
    "#category": ("imagehost", "pixhost", "gallery"),
    "#class"   : imagehosts.PixhostGalleryExtractor,
    "#pattern" : imagehosts.PixhostImageExtractor.pattern,
    "#count"   : 3,
},

)
