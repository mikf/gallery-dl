# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imgbox
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://imgbox.com/g/JaX5V5HX7g",
    "#category": ("", "imgbox", "gallery"),
    "#class"   : imgbox.ImgboxGalleryExtractor,
    "#sha1_url"     : "da4f15b161461119ee78841d4b8e8d054d95f906",
    "#sha1_metadata": "4b1e62820ac2c6205b7ad0b6322cc8e00dbe1b0c",
    "#sha1_content" : "d20307dc8511ac24d688859c55abf2e2cc2dd3cc",
},

{
    "#url"     : "https://imgbox.com/g/cUGEkRbdZZ",
    "#category": ("", "imgbox", "gallery"),
    "#class"   : imgbox.ImgboxGalleryExtractor,
    "#sha1_url"     : "76506a3aab175c456910851f66227e90484ca9f7",
    "#sha1_metadata": "fb0427b87983197849fb2887905e758f3e50cb6e",
},

{
    "#url"     : "https://imgbox.com/g/JaX5V5HX7h",
    "#category": ("", "imgbox", "gallery"),
    "#class"   : imgbox.ImgboxGalleryExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://imgbox.com/qHhw7lpG",
    "#category": ("", "imgbox", "image"),
    "#class"   : imgbox.ImgboxImageExtractor,
    "#results" : "https://images3.imgbox.com/6d/9a/qHhw7lpG_o.png",

    "#sha1_url"     : "ee9cdea6c48ad0161c1b5f81f6b0c9110997038c",
    "#sha1_metadata": "dfc72310026b45f3feb4f9cada20c79b2575e1af",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",

    "extension": "png",
    "filename" : "test-___-___",
    "image_key": "qHhw7lpG",
    "num"      : None,
},

{
    "#url"     : "https://imgbox.com/qHhw7lpH",
    "#category": ("", "imgbox", "image"),
    "#class"   : imgbox.ImgboxImageExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://images3.imgbox.com/6d/9a/qHhw7lpG_o.png",
    "#comment" : "direct link",
    "#class"   : imgbox.ImgboxImageExtractor,
    "#results" : "https://images3.imgbox.com/6d/9a/qHhw7lpG_o.png",

    "extension": "png",
    "filename" : "test-___-___",
    "image_key": "qHhw7lpG",
    "num"      : None,
},

{
    "#url"     : "https://i.imgbox.com/ivEi0Dgm.jpg",
    "#comment" : "direct link",
    "#class"   : imgbox.ImgboxImageExtractor,
    "#results" : "https://images3.imgbox.com/72/e9/ivEi0Dgm_o.jpg",

    "extension": "jpg",
    "filename" : "3998C2F200000578-3861564-image-a-25_1477114630790",
    "image_key": "ivEi0Dgm",
    "num"      : "1",
},

)
