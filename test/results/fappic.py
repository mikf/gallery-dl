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
    "#url"     : "https://www.fappic.com/98wxqcklyh8k/foo.bar",
    "#category": ("imagehost", "fappic", "image"),
    "#class"   : imagehosts.FappicImageExtractor,
    "#pattern"      : r"https://img\d+\.fappic\.com/img/\w+/test\.png",
    "#sha1_metadata": "433b1d310b0ff12ad8a71ac7b9d8ba3f8cd1e898",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",

    "filename"   : "test",
    "extension"  : "png",
    "token"      : "98wxqcklyh8k",
},

{
    "#url"     : "https://www.fappic.com/i/00133/qi2nplzmwq7d_t.jpg",
    "#comment" : "thumbnail URL (#8013)",
    "#category": ("imagehost", "fappic", "image"),
    "#class"   : imagehosts.FappicImageExtractor,
    "#results" : "https://fappic.com/img/lahcoyienda2ftjqkmgdzxiaykeddwewwzw27nbuje/1X08WLv-4q6_0090.jpeg",

    "filename" : "1X08WLv-4q6_0090",
    "extension": "jpeg",
    "token"    : "qi2nplzmwq7d",
},

)
