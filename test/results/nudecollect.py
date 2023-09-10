# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import nudecollect


__tests__ = (
{
    "#url"     : "https://www.nudecollect.com/content/20201220_Teenpornstorage_Patritcy_Vanessa_Lesbian_Lust/image-4-pics-108-mirror-43.html",
    "#category": ("", "nudecollect", "image"),
    "#class"   : nudecollect.NudecollectImageExtractor,
    "#pattern" : r"https://mirror\d+\.nudecollect\.com/showimage/nudecollect-8769086487/image00004-5896498214-43-9689595623/20201220_Teenpornstorage_Patritcy_Vanessa_Lesbian_Lust/9879560327/nudecollect\.com\.jpg",

    "slug"  : "20201220_Teenpornstorage_Patritcy_Vanessa_Lesbian_Lust",
    "title" : "20201220 Teenpornstorage Patritcy Vanessa Lesbian Lust",
    "num"   : 4,
    "count" : 108,
    "mirror": 43,
},

{
    "#url"     : "https://www.nudecollect.com/content/20201220_Teenpornstorage_Patritcy_Vanessa_Lesbian_Lust/image-10-pics-108-mirror-43.html",
    "#category": ("", "nudecollect", "image"),
    "#class"   : nudecollect.NudecollectImageExtractor,
},

{
    "#url"     : "https://www.nudecollect.com/content/20170219_TheWhiteBoxxx_Caprice_Tracy_Loves_Hot_ass_fingering_and_sensual_lesbian_sex_with_alluring_Czech_babes_x125_1080px/index-mirror-67-125.html",
    "#category": ("", "nudecollect", "album"),
    "#class"   : nudecollect.NudecollectAlbumExtractor,
    "#pattern" : r"https://mirror\d+\.nudecollect\.com/showimage/nudecollect-8769086487/image00\d\d\d-5896498214-67-9689595623/20170219_TheWhiteBoxxx_Caprice_Tracy_Loves_Hot_ass_fingering_and_sensual_lesbian_sex_with_alluring_Czech_babes_x125_1080px/9879560327/nudecollect\.com\.jpg",
    "#count"   : 125,

    "slug"  : "20170219_TheWhiteBoxxx_Caprice_Tracy_Loves_Hot_ass_fingering_and_sensual_lesbian_sex_with_alluring_Czech_babes_x125_1080px",
    "title" : "20170219 TheWhiteBoxxx Caprice Tracy Loves Hot ass fingering and sensual lesbian sex with alluring Czech babes x125 1080px",
    "num"   : int,
    "mirror": 67,
},

{
    "#url"     : "https://www.nudecollect.com/content/20201220_Teenpornstorage_Patritcy_Vanessa_Lesbian_Lust/page-1-pics-108-mirror-43.html",
    "#category": ("", "nudecollect", "album"),
    "#class"   : nudecollect.NudecollectAlbumExtractor,
    "#pattern" : r"https://mirror\d+\.nudecollect\.com/showimage/nudecollect-8769086487/image00\d\d\d-5896498214-43-9689595623/20201220_Teenpornstorage_Patritcy_Vanessa_Lesbian_Lust/9879560327/nudecollect\.com\.jpg",
    "#count"   : 108,

    "slug"  : "20201220_Teenpornstorage_Patritcy_Vanessa_Lesbian_Lust",
    "title" : "20201220 Teenpornstorage Patritcy Vanessa Lesbian Lust",
    "num"   : int,
    "mirror": 43,
},

)
