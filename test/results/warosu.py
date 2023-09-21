# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import warosu


__tests__ = (
{
    "#url"     : "https://warosu.org/jp/thread/16656025",
    "#category": ("", "warosu", "thread"),
    "#class"   : warosu.WarosuThreadExtractor,
    "#sha1_url"     : "889d57246ed67e491e5b8f7f124e50ea7991e770",
    "#sha1_metadata": "c00ea4c5460c5986994f17bb8416826d42ca57c0",
},

{
    "#url"     : "https://warosu.org/jp/thread/16658073",
    "#category": ("", "warosu", "thread"),
    "#class"   : warosu.WarosuThreadExtractor,
    "#sha1_url"     : "4500cf3184b067424fd9883249bd543c905fbecd",
    "#sha1_metadata": "7534edf4ec51891dbf44d775b73fbbefd52eec71",
    "#sha1_content" : "d48df0a701e6599312bfff8674f4aa5d4fb8db1c",
},

)
