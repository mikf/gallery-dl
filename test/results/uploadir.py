# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import uploadir


__tests__ = (
{
    "#url"     : "https://uploadir.com/u/rd3t46ry",
    "#comment" : "image",
    "#category": ("", "uploadir", "file"),
    "#class"   : uploadir.UploadirFileExtractor,
    "#pattern" : r"https://uploadir\.com/u/rd3t46ry",
    "#count"   : 1,

    "extension": "jpg",
    "filename" : "Chloe and Rachel 4K jpg",
    "id"       : "rd3t46ry",
},

{
    "#url"     : "https://uploadir.com/uploads/gxe8ti9v/downloads/new",
    "#comment" : "archive",
    "#category": ("", "uploadir", "file"),
    "#class"   : uploadir.UploadirFileExtractor,
    "#pattern" : r"https://uploadir\.com/uploads/gxe8ti9v/downloads",
    "#count"   : 1,

    "extension": "zip",
    "filename" : "NYAN-Mods-Pack#1",
    "id"       : "gxe8ti9v",
},

{
    "#url"     : "https://uploadir.com/u/fllda6xl",
    "#comment" : "utf-8 filename",
    "#category": ("", "uploadir", "file"),
    "#class"   : uploadir.UploadirFileExtractor,
    "#pattern" : r"https://uploadir\.com/u/fllda6xl",
    "#count"   : 1,

    "extension": "png",
    "filename" : "_圖片_🖼_image_",
    "id"       : "fllda6xl",
},

{
    "#url"     : "https://uploadir.com/uploads/rd3t46ry",
    "#category": ("", "uploadir", "file"),
    "#class"   : uploadir.UploadirFileExtractor,
},

{
    "#url"     : "https://uploadir.com/user/uploads/rd3t46ry",
    "#category": ("", "uploadir", "file"),
    "#class"   : uploadir.UploadirFileExtractor,
},

)
