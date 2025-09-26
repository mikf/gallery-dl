# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import chevereto


__tests__ = (
{
    "#url"     : "https://imglike.com/image/EMT-Skills-Verification-by-EMSA.Lx6dT",
    "#category": ("chevereto", "imglike", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
    "#results" : "https://imglike.com/images/2022/08/12/EMT-Skills-Verification-by-EMSA.gif",

    "album"    : "",
    "date"     : "dt:2022-08-12 06:36:10",
    "extension": "gif",
    "filename" : "EMT-Skills-Verification-by-EMSA",
    "id"       : "Lx6dT",
    "url"      : "https://imglike.com/images/2022/08/12/EMT-Skills-Verification-by-EMSA.gif",
    "user"     : "albertthomas9",
},

{
    "#url"     : "https://www.imglike.com/image/EMT-Skills-Verification-by-EMSA.Lx6dT",
    "#category": ("chevereto", "imglike", "image"),
    "#class"   : chevereto.CheveretoImageExtractor,
},

{
    "#url"     : "https://imglike.com/albertthomas9",
    "#category": ("chevereto", "imglike", "user"),
    "#class"   : chevereto.CheveretoUserExtractor,
    "#results" : (
        "https://imglike.com/image/Palm-Desert-Resuscitation-Education-%28YourCPRMD.com%29.L1xHc",
        "https://imglike.com/image/CNA-Programs-Near-Me-Anza.L1VES",
        "https://imglike.com/image/EMT-Skills-Verification-by-EMSA.Lx6dT",
        "https://imglike.com/image/American-Heart-Association-BLS.Lisl2",
    ),
},

{
    "#url"     : "https://imglike.com/album/Kara-Del-Toro-Naked.cG7l",
    "#category": ("chevereto", "imglike", "album"),
    "#class"   : chevereto.CheveretoAlbumExtractor,
    "#results" : (
        "https://imglike.com/image/Nude-Kara-Del-Tori-%286%29.LGXgd",
        "https://imglike.com/image/Nude-Kara-Del-Tori-%285%29.LGxFT",
        "https://imglike.com/image/Nude-Kara-Del-Tori-%283%29.LGB1z",
        "https://imglike.com/image/Nude-Kara-Del-Tori-%284%29.LG6lR",
        "https://imglike.com/image/Nude-Kara-Del-Tori-%282%29.LG4Jg",
        "https://imglike.com/image/Nude-Kara-Del-Tori-%281%29.LGP7s",
    ),
},

{
    "#url"     : "https://imglike.com/category/Bursting-boobs",
    "#category": ("chevereto", "imglike", "category"),
    "#class"   : chevereto.CheveretoCategoryExtractor,
    "#pattern" : chevereto.CheveretoImageExtractor.pattern,
    "#range"   : "1-100",
    "#count"   : 100,
},

)
