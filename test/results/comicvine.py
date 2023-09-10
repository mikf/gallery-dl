# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import comicvine


__tests__ = (
{
    "#url"     : "https://comicvine.gamespot.com/jock/4040-5653/images/",
    "#category": ("", "comicvine", "tag"),
    "#class"   : comicvine.ComicvineTagExtractor,
    "#pattern" : r"https://comicvine\.gamespot\.com/a/uploads/original/\d+/\d+/\d+-.+\.(jpe?g|png)",
    "#count"   : ">= 140",
},

{
    "#url"     : "https://comicvine.gamespot.com/batman/4005-1699/images/?tag=Fan%20Art%20%26%20Cosplay",
    "#category": ("", "comicvine", "tag"),
    "#class"   : comicvine.ComicvineTagExtractor,
    "#pattern" : r"https://comicvine\.gamespot\.com/a/uploads/original/\d+/\d+/\d+-.+",
    "#count"   : ">= 450",
},

)
