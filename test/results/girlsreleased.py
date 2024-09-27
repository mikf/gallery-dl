# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import girlsreleased
import datetime


__tests__ = (
{
    "#url"     : "https://girlsreleased.com/set/32332",
    "#category": ("", "girlsreleased", "set"),
    "#class"   : girlsreleased.GirlsreleasedSetExtractor,
    "#count"   : 122,

    "id"        : "32332",
    "title"     : "Monadiko",
    "model"     : ["Mia Sollis"],
    "site"      : "sexart.com",
    "date"      : datetime.datetime,
},

{
    "#url"     : "https://girlsreleased.com/set/124943",
    "#category": ("", "girlsreleased", "set"),
    "#class"   : girlsreleased.GirlsreleasedSetExtractor,
    "#count"   : 79,

    "id"        : "124943",
    "title"     : "124943",
    "model"     : ["Iveta"],
    "site"      : "errotica-archives.com",
    "date"      : datetime.datetime,
},

{
    "#url"     : "https://girlsreleased.com/model/11545/Ariana%20Regent",
    "#category": ("", "girlsreleased", "model"),
    "#class"   : girlsreleased.GirlsreleasedModelExtractor,
},

{
    "#url"     : "https://girlsreleased.com/site/amourangels.com",
    "#category": ("", "girlsreleased", "site"),
    "#class"   : girlsreleased.GirlsreleasedSiteExtractor,
},

{
    "#url"     : "https://girlsreleased.com/site/femjoy.com/model/854/Gabi",
    "#category": ("", "girlsreleased", "site"),
    "#class"   : girlsreleased.GirlsreleasedSiteExtractor,
},
)
