# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hbrowse


__tests__ = (
{
    "#url"     : "https://www.hbrowse.com/10363/c00000",
    "#category": ("", "hbrowse", "chapter"),
    "#class"   : hbrowse.HbrowseChapterExtractor,
    "#sha1_url"     : "6feefbc9f4b98e20d8425ddffa9dd111791dc3e6",
    "#sha1_metadata": "274996f6c809e5250b6ff3abbc5147e29f89d9a5",
    "#sha1_content" : "44578ebbe176c2c27434966aef22945787e2781e",
},

{
    "#url"     : "https://www.hbrowse.com/10363",
    "#category": ("", "hbrowse", "manga"),
    "#class"   : hbrowse.HbrowseMangaExtractor,
    "#sha1_url"     : "b89682bfb86c11d2af0dc47463804ec3ac4aadd6",
    "#sha1_metadata": "4b15fda1858a69de1fbf5afddfe47dd893397312",
},

)
