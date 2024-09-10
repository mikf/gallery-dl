# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import cohost


__tests__ = (
{
    "#url"     : "https://cohost.org/infinitebrians",
    "#category": ("", "cohost", "user"),
    "#class"   : cohost.CohostUserExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://cohost.org/infinitebrians/post/4957017-thank-you-akira-tori",
    "#category": ("", "cohost", "post"),
    "#class"   : cohost.CohostPostExtractor,
    "#urls"    : "https://staging.cohostcdn.org/attachment/58f9aa96-d2b2-4838-b81c-9aa8bac0bea0/march%204%202024.png",
},

)
