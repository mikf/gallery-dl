# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import noop


__tests__ = (
{
    "#url"     : "noop",
    "#class"   : noop.NoopExtractor,
    "#urls"    : (),
    "#count"   : 0,
},

{
    "#url"     : "nop",
    "#class"   : noop.NoopExtractor,
},

{
    "#url"     : "NOOP",
    "#class"   : noop.NoopExtractor,
},

)
