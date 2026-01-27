# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import listal


__tests__ = (
{
    "#url"     : "https://www.listal.com/viewimage/29620846",
    "#class"   : listal.ListalImageExtractor,
    "#results" : "https://ilarge.lisimg.com/image/29620846/1030full-jim-carrey.jpg",

    "author"    : "sinaia16",
    "author_url": "https://sinaia16.listal.com",
    "date"      : "dt:2024-07-18 18:50:00",
    "extension" : "jpg",
    "filename"  : "1030full-jim-carrey",
    "height"    : 1037,
    "id"        : "29620846",
    "title"     : "Jim Carrey",
    "url"       : "https://ilarge.lisimg.com/image/29620846/1030full-jim-carrey.jpg",
    "width"     : 1030,
},

{
    "#url"     : "https://www.listal.com/jim-carrey/pictures",
    "#class"   : listal.ListalPeopleExtractor,
    "#pattern" : r"https://i\w+\.lisimg\.com/image/\d+/\d+full-.+\.jpg",
    "#range"   : "1-10",
    "#count"   : 10,

    "author"    : str,
    "author_url": r"re:https://\w+.listal.com",
    "date"      : "type:datetime",
    "extension" : "jpg",
    "filename"  : str,
    "width"     : range(200, 2000),
    "height"    : range(200, 2000),
    "id"        : r"re:\d+",
    "title"     : "Jim Carrey",
    "url"       : r"re:https://.+",
},

)
