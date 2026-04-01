# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gdl_ext import A


__tests__ = (
{
    "#url"     : "asd:",
    "#class"   : A,

    "asd": 123,
},

{
    "#url"     : "asd:asd",
    "#class"   : A,
},

{
    "#url"     : "asd:qwe",
    "#class"   : A,
},

)
