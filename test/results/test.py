# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import test


__tests__ = (
{
    "#url"     : "test:pixiv",
    "#category": ("", "test", ""),
    "#class"   : test.TestExtractor,
},

{
    "#url"     : "test:pixiv:user,favorite:0",
    "#category": ("", "test", ""),
    "#class"   : test.TestExtractor,
},

{
    "#url"     : "test:",
    "#category": ("", "test", ""),
    "#class"   : test.TestExtractor,
},

)
