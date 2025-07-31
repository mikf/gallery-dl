# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://picstate.com/view/full/21812181_qxtpb",
    "#category": ("imagehost", "picstate", "image"),
    "#class"   : imagehosts.PicstateImageExtractor,
},

{
    "#url"     : "https://picstate.com/view/full/21812181_qxtpb",
    "#category": ("imagehost", "picstate", "image"),
    "#class"   : imagehosts.PicstateImageExtractor,
    "#pattern"      : r"https://picstate.com/files/\w+/\w+.\w+",
    "#sha1_content" : "bbb2b257049633f450660c88b75813c8c39612b1",
    "#sha1_metadata": "68f331e95977d71cd7d615f259359ef3bbb8f163"
},
)
