# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import slickpic


__tests__ = (
{
    "#url"     : "https://mattcrandall.slickpic.com/albums/LamborghiniMurcielago/",
    "#category": ("", "slickpic", "album"),
    "#class"   : slickpic.SlickpicAlbumExtractor,
    "#pattern"      : r"https://stored-cf\.slickpic\.com/NDk5MjNmYTc1MzU0MQ,,/20160807/\w+/p/o/JSBFSS-\d+\.jpg",
    "#count"        : 102,
    "#sha1_metadata": "c37c4ce9c54c09abc6abdf295855d46f11529cbf",
},

{
    "#url"     : "https://mattcrandall.slickpic.com/albums/LamborghiniMurcielago/",
    "#category": ("", "slickpic", "album"),
    "#class"   : slickpic.SlickpicAlbumExtractor,
    "#range"       : "34",
    "#sha1_content": [
        "276eb2c902187bb177ae8013e310e1d6641fba9a",
        "52b5a310587de1048030ab13a912f6a3a9cc7dab",
        "cec6630e659dc72db1ee1a9a6f3b525189261988",
        "6f81e1e74c6cd6db36844e7211eef8e7cd30055d",
        "22e83645fc242bc3584eca7ec982c8a53a4d8a44",
    ],
},

{
    "#url"     : "https://mattcrandall.slickpic.com/gallery/",
    "#category": ("", "slickpic", "user"),
    "#class"   : slickpic.SlickpicUserExtractor,
    "#pattern" : slickpic.SlickpicAlbumExtractor.pattern,
    "#count"   : ">= 358",
},

{
    "#url"     : "https://mattcrandall.slickpic.com/",
    "#category": ("", "slickpic", "user"),
    "#class"   : slickpic.SlickpicUserExtractor,
},

)
