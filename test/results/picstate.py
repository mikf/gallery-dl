# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://picstate.com/view/full/23416694_sfyue",
    "#class"   : imagehosts.PicstateImageExtractor,
    "#results"      : "https://picstate.com/file/23416694_sfyue/test-___-_22__.png",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",

    "filename"   : "test-___-_22__",
    "extension"  : "png",
    "token"      : "23416694_sfyue",
},

{
    "#url"     : "https://picstate.com/view/full/21812181_qxtpb",
    "#class"   : imagehosts.PicstateImageExtractor,
    "#results"      : "https://picstate.com/files/21812181_qxtpb/0.jpg",
    "#sha1_content" : "bbb2b257049633f450660c88b75813c8c39612b1",
    "#sha1_metadata": "68f331e95977d71cd7d615f259359ef3bbb8f163",

    "filename"   : "0",
    "extension"  : "jpg",
    "token"      : "21812181_qxtpb",
},

)
