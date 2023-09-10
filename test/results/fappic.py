# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://fappic.com/98wxqcklyh8k/test.png",
    "#category": ("imagehost", "fappic", "image"),
    "#class"   : imagehosts.FappicImageExtractor,
},

{
    "#url"     : "https://www.fappic.com/98wxqcklyh8k/test.png",
    "#category": ("imagehost", "fappic", "image"),
    "#class"   : imagehosts.FappicImageExtractor,
    "#pattern"      : r"https://img\d+\.fappic\.com/img/\w+/test\.png",
    "#sha1_metadata": "433b1d310b0ff12ad8a71ac7b9d8ba3f8cd1e898",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",
},

)
