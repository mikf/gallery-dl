# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import philomena


__tests__ = (
{
    "#url"     : "philomena:https://manebooru.art/307071",
    "#comment" : "'view_url' yields 404 (#6922)",
    "#category": ("philomena", "manebooru.art", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
    "#results"     : "https://static.manebooru.art/img/view/2020/10/27/307071.png",
    "#sha1_content": "82c21bfb2675449893fa4b2546546f404019b3c8",

    "date"     : "dt:2020-10-27 11:58:40"
},

{
    "#url"     : "philomena:https://ponerpics.org/images/1",
    "#category": ("philomena", "ponerpics.org", "post"),
    "#class"   : philomena.PhilomenaPostExtractor,
    "#results" : "https://ponerpics.org/img/view/2012/1/2/1.png",

    "date"     : "dt:2012-01-02 03:12:33"
},

)
